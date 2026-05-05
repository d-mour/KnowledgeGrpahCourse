#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
import zipfile
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from xml.etree.ElementTree import Element, SubElement, ElementTree

PROJECT_DIR = Path(__file__).resolve().parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
EXPORT_DIR = PROJECT_DIR / "exports"
APP_DIR = PROJECT_DIR / "app"
APP_DATA_DIR = APP_DIR / "data"
HF_CACHE_DIR = Path(os.environ.get("HF_DATASETS_CACHE", "D:/hf_cache" if os.name == "nt" else str(RAW_DIR / "hf_cache")))

BC5CDR_DATASET = "bigbio/bc5cdr"
BC5CDR_CONFIG = "bc5cdr_bigbio_kb"
CIRCOR_URL = "https://physionet.org/files/circor-heart-sound/1.0.3/training_data/"
ICBHI_ZIP_URL = "https://bhichallenge.med.auth.gr/sites/default/files/ICBHI_final_database/ICBHI_final_database.zip"
IMAGE_DATASET_DEFAULT = "hf-vision/chest-xray-pneumonia"
IMAGE_SPLIT_DEFAULT = "train"
EX_BASE = "https://example.org/medical-multimodal-kg/"

TABLES = [
    "DATASET_STATS", "CASE_META",
    "TXT_DOC", "TXT_SEG", "TXT_LEMMA", "TXT_POS", "TXT_DEP",
    "TXT_NER", "TXT_NORM", "TXT_REL", "TXT_ASSERT", "TXT_TOPIC",
    "AUD_META", "AUD_SEG", "AUD_EVT", "AUD_QLT",
    "IMG_STRUCT", "IMG_FINDING", "IMG_ATTR",
    "MM_ALIGN",
    "PRM_INPUT", "PRM_TOOL", "PRM_OUTPUT", "RSN_GRAPH", "EVAL_LAYER",
]
STATE_MAP_CIRCOR = {0: "unannotated", 1: "S1", 2: "systole", 3: "S2", 4: "diastole"}


def log(msg: str) -> None:
    print(msg, flush=True)


def ensure_dirs() -> None:
    for p in [RAW_DIR, EXPORT_DIR / "csv", EXPORT_DIR / "json", EXPORT_DIR / "xml", EXPORT_DIR / "rdf", EXPORT_DIR / "sparql", APP_DIR, APP_DATA_DIR, APP_DATA_DIR / "audio", APP_DATA_DIR / "images"]:
        p.mkdir(parents=True, exist_ok=True)


def safe_id(x: Any, max_len: int = 140) -> str:
    s = str(x if x is not None else "").strip()
    s = re.sub(r"\s+", "_", s)
    s = re.sub(r"[^A-Za-z0-9А-Яа-яёЁ_.:-]+", "_", s)
    s = s.strip("_") or "x"
    return s[:max_len]


def as_text(x: Any) -> str:
    if x is None:
        return ""
    if isinstance(x, list):
        return " ".join(str(v) for v in x)
    return str(x)


def dumps(x: Any) -> str:
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


def get_span(obj: Dict[str, Any]) -> Tuple[Optional[int], Optional[int]]:
    offs = obj.get("offsets", obj.get("offset"))
    txt = as_text(obj.get("text", ""))
    if offs is None:
        return None, None
    if isinstance(offs, int):
        return offs, offs + len(txt)
    if isinstance(offs, list):
        if not offs:
            return None, None
        if isinstance(offs[0], (list, tuple)):
            starts = [int(v[0]) for v in offs if len(v) >= 2]
            ends = [int(v[1]) for v in offs if len(v) >= 2]
            return (min(starts), max(ends)) if starts and ends else (None, None)
        if len(offs) == 2 and all(isinstance(v, (int, float)) for v in offs):
            return int(offs[0]), int(offs[1])
        if len(offs) == 1 and isinstance(offs[0], (int, float)):
            return int(offs[0]), int(offs[0]) + len(txt)
    return None, None


def relation_args(rel: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    for a, b in [("arg1_id", "arg2_id"), ("source_id", "target_id"), ("subject_id", "object_id")]:
        if a in rel and b in rel:
            return as_text(rel.get(a)), as_text(rel.get(b))
    nodes = rel.get("nodes")
    if isinstance(nodes, list) and len(nodes) >= 2:
        return as_text(nodes[0].get("refid") or nodes[0].get("id")), as_text(nodes[1].get("refid") or nodes[1].get("id"))
    return None, None


def norm_list(x: Any) -> List[Any]:
    if x is None:
        return []
    return x if isinstance(x, list) else [x]


def empty_tables() -> Dict[str, List[Dict[str, Any]]]:
    return {name: [] for name in TABLES}


class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: List[str] = []
    def handle_starttag(self, tag, attrs):
        if tag.lower() == "a":
            href = dict(attrs).get("href")
            if href:
                self.links.append(href)


def download_file(url: str, out: Path, overwrite: bool = False) -> Path:
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists() and out.stat().st_size > 0 and not overwrite:
        log(f"[download] exists: {out}")
        return out
    log(f"[download] {url}")
    tmp = out.with_suffix(out.suffix + ".part")
    with requests.get(url, stream=True, timeout=90, verify=False) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", 0) or 0)
        done = 0
        with tmp.open("wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                done += len(chunk)
                if total and done % (200 * 1024 * 1024) < 1024 * 1024:
                    log(f"  {done/1024/1024:.0f}/{total/1024/1024:.0f} MB")
    tmp.replace(out)
    return out


def download_circor(out_dir: Path, include_wav: bool = False) -> Path:
    import requests
    out_dir.mkdir(parents=True, exist_ok=True)
    parser = LinkParser()
    parser.feed(requests.get(CIRCOR_URL, timeout=60).text)
    allowed = {".txt", ".tsv", ".hea", ".csv"}
    if include_wav:
        allowed.add(".wav")
    names = []
    for href in parser.links:
        name = urllib.parse.unquote(href.split("?")[0].split("#")[0])
        if name.endswith("/") or name == "../":
            continue
        if Path(name).suffix.lower() in allowed:
            names.append(Path(name).name)
    names = sorted(set(names))
    log(f"[CirCor] files to download/check: {len(names)}")
    for i, name in enumerate(names, start=1):
        try:
            download_file(urllib.parse.urljoin(CIRCOR_URL, name), out_dir / name)
        except Exception as e:
            log(f"[CirCor][WARN] {name}: {e}")
        if i % 200 == 0:
            log(f"[CirCor] checkpoint {i}/{len(names)}")
    return out_dir


def download_icbhi(out_dir: Path, source: str = "direct") -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    if source == "local":
        log("[ICBHI] local mode")
        return out_dir
    if source == "direct":
        z = download_file(ICBHI_ZIP_URL, out_dir / "ICBHI_final_database.zip")
        marker = out_dir / ".unzipped"
        if not marker.exists():
            log("[ICBHI] unzip...")
            with zipfile.ZipFile(z) as zf:
                zf.extractall(out_dir)
            marker.write_text("ok", encoding="utf-8")
        return out_dir
    if source == "kaggle":
        slugs = [
            "husninm/icbhi-2017-challenge",
            "vbookshelf/respiratory-sound-database",
            "nimalanparameshwaran/icbhi-2017-challenge-respiratory-sound-database",
        ]
        last = None
        for slug in slugs:
            try:
                subprocess.check_call([sys.executable, "-m", "kaggle", "datasets", "download", "-d", slug, "-p", str(out_dir), "--unzip"])
                return out_dir
            except Exception as e:
                last = e
                log(f"[ICBHI][WARN] Kaggle failed {slug}: {e}")
        raise RuntimeError(f"Kaggle failed: {last}")
    raise ValueError(source)


def ensure_spacy(model_name: str):
    import spacy
    try:
        return spacy.load(model_name)
    except OSError:
        from spacy.cli import download
        log(f"[spaCy] downloading {model_name}")
        download(model_name)
        return spacy.load(model_name)


def extract_local_entities(doc: Dict[str, Any], passage: Dict[str, Any]) -> List[Dict[str, Any]]:
    text = as_text(passage.get("text", ""))
    ps, pe = get_span(passage)
    if ps is None:
        ps, pe = 0, len(text)
    out = []
    for ent in doc.get("entities", []):
        es, ee = get_span(ent)
        if es is None or ee is None:
            continue
        if es >= ps and ee <= pe:
            d = dict(ent)
            d["local_start"] = int(es - ps)
            d["local_end"] = int(ee - ps)
            out.append(d)
    return out


def extract_local_relations(doc: Dict[str, Any], ents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    ids = {as_text(e.get("id")) for e in ents}
    out = []
    for rel in doc.get("relations", []):
        a, b = relation_args(rel)
        if a in ids and b in ids:
            out.append(rel)
    return out


def build_text_tables(tables: Dict[str, List[Dict[str, Any]]], limit: int = 0, spacy_model: str = "en_core_web_sm") -> None:
    from datasets import load_dataset
    ds = load_dataset(BC5CDR_DATASET, name=BC5CDR_CONFIG, trust_remote_code=True, cache_dir=str(HF_CACHE_DIR))
    nlp = ensure_spacy(spacy_model)
    n_pass = 0
    for split_name in [s for s in ["train", "validation", "test"] if s in ds]:
        for doc in ds[split_name]:
            source_id = as_text(doc.get("id"))
            case_id = f"case_bc5cdr_{safe_id(source_id)}"
            tables["CASE_META"].append({
                "case_id": case_id, "patient_pseudo_id": "", "encounter_id": "",
                "dataset": "BC5CDR", "modality": "text", "source_id": source_id,
                "description": "PubMed abstract with chemical/disease entities and CID relations",
            })
            for p_idx, passage in enumerate(doc.get("passages", []) or []):
                if limit and n_pass >= limit:
                    log(f"[text] limit reached: {limit}")
                    return
                text = as_text(passage.get("text", ""))
                if not text.strip():
                    continue
                ps, pe = get_span(passage)
                if ps is None:
                    ps, pe = 0, len(text)
                doc_id = f"txtdoc_{safe_id(source_id)}_p{p_idx}"
                tables["TXT_DOC"].append({
                    "case_id": case_id, "doc_id": doc_id, "source_dataset": "BC5CDR",
                    "split": split_name, "source_doc_id": source_id, "passage_index": p_idx,
                    "char_start_global": ps, "char_end_global": pe, "text": text,
                })
                ents = sorted(extract_local_entities(doc, passage), key=lambda e: (e.get("local_start", 0), e.get("local_end", 0)))
                rels = extract_local_relations(doc, ents)
                ent_map = {}
                for i, ent in enumerate(ents):
                    ent_id = as_text(ent.get("id", i))
                    mention_id = f"mention_{safe_id(doc_id)}_{safe_id(ent_id)}"
                    ent_map[ent_id] = mention_id
                    ent_text = as_text(ent.get("text"))
                    ent_type = as_text(ent.get("type", "Entity"))
                    tables["TXT_NER"].append({
                        "case_id": case_id, "doc_id": doc_id, "mention_id": mention_id,
                        "source_entity_id": ent_id, "span_start": ent.get("local_start"),
                        "span_end": ent.get("local_end"), "text": ent_text,
                        "entity_type": ent_type, "source": "BC5CDR gold",
                    })
                    norms = norm_list(ent.get("normalized")) or [{}]
                    for norm in norms:
                        kb_name, concept_id = "", ""
                        if isinstance(norm, dict):
                            kb_name = as_text(norm.get("db_name"))
                            concept_id = as_text(norm.get("db_id"))
                        else:
                            concept_id = as_text(norm)
                        tables["TXT_NORM"].append({
                            "mention_id": mention_id, "kb_name": kb_name,
                            "concept_id": concept_id, "normalized_text": ent_text,
                        })
                    tables["TXT_ASSERT"].append({
                        "mention_id": mention_id, "negated": False, "certainty": "asserted",
                        "source": "gold", "temporality": "not_specified",
                    })
                for r_idx, rel in enumerate(rels):
                    a, b = relation_args(rel)
                    if a in ent_map and b in ent_map:
                        tables["TXT_REL"].append({
                            "case_id": case_id, "doc_id": doc_id,
                            "relation_id": f"rel_{safe_id(doc_id)}_{safe_id(rel.get('id', r_idx))}",
                            "relation_type": as_text(rel.get("type", "relation")),
                            "mention_id_src": ent_map[a], "mention_id_tgt": ent_map[b],
                            "source_relation_id": as_text(rel.get("id", "")),
                        })
                tables["TXT_TOPIC"].append({
                    "case_id": case_id, "doc_id": doc_id,
                    "topic": "chemical-disease relation" if rels else "biomedical entity mentions",
                    "score": 1.0 if rels else 0.75,
                    "entity_type_counts": dumps(dict(Counter(as_text(e.get("type")) for e in ents))),
                })
                parsed = nlp(text)
                sent_by_i = {}
                sent_no = 0
                for sent in parsed.sents:
                    sent_no += 1
                    for tok in sent:
                        sent_by_i[tok.i] = sent_no
                token_id = {tok.i: f"tok_{safe_id(doc_id)}_{tok.i}" for tok in parsed}
                for tok in parsed:
                    tid = token_id[tok.i]
                    tables["TXT_SEG"].append({
                        "case_id": case_id, "doc_id": doc_id,
                        "sent_id": f"{doc_id}_s{sent_by_i.get(tok.i, 0)}",
                        "token_id": tid, "token_index": tok.i, "text": tok.text,
                        "char_start": tok.idx, "char_end": tok.idx + len(tok.text),
                    })
                    tables["TXT_LEMMA"].append({"token_id": tid, "lemma": tok.lemma_})
                    tables["TXT_POS"].append({"token_id": tid, "upos": tok.pos_, "xpos": tok.tag_, "morph": str(tok.morph)})
                    tables["TXT_DEP"].append({"token_id": tid, "head_id": "" if tok.dep_ == "ROOT" else token_id.get(tok.head.i, ""), "dep": tok.dep_})
                n_pass += 1
                if n_pass % 100 == 0:
                    log(f"[text] passages={n_pass}")
    log(f"[text] done passages={n_pass}")


def sf_info(path: Path) -> Dict[str, Any]:
    try:
        import soundfile as sf
        info = sf.info(str(path))
        return {"samplerate": info.samplerate, "channels": info.channels, "duration_sec": info.frames / info.samplerate if info.samplerate else "", "frames": info.frames}
    except Exception as e:
        return {"samplerate": "", "channels": "", "duration_sec": "", "frames": "", "error": str(e)}


def audio_quality(path: Path, compute: bool) -> Dict[str, Any]:
    if not compute:
        return {"quality_flag": "not_calculated", "peak": "", "rms": "", "silence_ratio": "", "clipping_ratio": ""}
    try:
        import numpy as np
        import soundfile as sf
        y, sr = sf.read(str(path), always_2d=False)
        if getattr(y, "ndim", 1) > 1:
            y = y.mean(axis=1)
        y = y[: min(len(y), int(sr * 20))].astype("float64")
        peak = float(np.max(np.abs(y))) if len(y) else 0.0
        rms = float(np.sqrt(np.mean(y * y))) if len(y) else 0.0
        silence = float(np.mean(np.abs(y) < 0.01)) if len(y) else 1.0
        clipping = float(np.mean(np.abs(y) > 0.99 * peak)) if peak > 0 else 0.0
        flag = "possible_clipping" if clipping > 0.01 else "possibly_low_signal" if silence > 0.7 else "usable"
        return {"quality_flag": flag, "peak": peak, "rms": rms, "silence_ratio": silence, "clipping_ratio": clipping}
    except Exception as e:
        return {"quality_flag": "error", "error": str(e), "peak": "", "rms": "", "silence_ratio": "", "clipping_ratio": ""}


def parse_circor_patient_txt(path: Path) -> Tuple[Dict[str, str], List[Dict[str, str]]]:
    meta = {"patient_id": path.stem}
    recs = []
    for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("#"):
            line = line[1:].strip()
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        else:
            parts = line.split()
            if len(parts) >= 3 and parts[1].lower().endswith(".wav"):
                recs.append({"patient_id": path.stem, "site": parts[0], "wav_file": parts[1], "tsv_file": parts[2]})
            elif len(parts) >= 4 and parts[2].lower().endswith(".wav"):
                recs.append({"patient_id": path.stem, "site": parts[1], "wav_file": parts[2], "tsv_file": parts[3]})
    return meta, recs


def read_circor_tsv(path: Path) -> List[Dict[str, Any]]:
    out = []
    if not path.exists():
        return out
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        parts = re.split(r"\s+", line.strip())
        if len(parts) < 3:
            continue
        try:
            state_id = int(float(parts[2]))
            out.append({
                "idx": i, "time_start": float(parts[0]), "time_end": float(parts[1]),
                "state_id": state_id, "state_name": STATE_MAP_CIRCOR.get(state_id, f"state_{state_id}"),
            })
        except Exception:
            pass
    return out


def find_dir_with_files(root: Path, suffixes: Tuple[str, ...]) -> Optional[Path]:
    if not root.exists():
        return None
    best, best_n = None, -1
    for p in root.rglob("*"):
        if p.is_dir():
            n = sum(len(list(p.glob("*" + s))) for s in suffixes)
            if n > best_n:
                best, best_n = p, n
    return best if best_n > 0 else None


def build_circor_tables(tables: Dict[str, List[Dict[str, Any]]], root: Path, limit: int = 0, compute_quality: bool = False) -> None:
    if not root or not root.exists():
        log(f"[CirCor] missing dir: {root}")
        return
    n = 0
    for txt in sorted(root.glob("*.txt")):
        meta, recs = parse_circor_patient_txt(txt)
        if not recs:
            for wav in sorted(root.glob(f"{txt.stem}_*.wav")):
                recs.append({"patient_id": txt.stem, "site": wav.stem.split("_")[-1], "wav_file": wav.name, "tsv_file": wav.with_suffix(".tsv").name})
        for rec in recs:
            if limit and n >= limit:
                log(f"[CirCor] limit reached: {limit}")
                return
            wav = root / rec["wav_file"]
            if not wav.exists():
                continue
            patient = rec["patient_id"]
            case_id = f"case_circor_{safe_id(patient)}"
            audio_id = f"circor_{safe_id(wav.stem)}"
            info = sf_info(wav)
            q = audio_quality(wav, compute_quality)
            tables["CASE_META"].append({"case_id": case_id, "patient_pseudo_id": safe_id(patient), "encounter_id": "", "dataset": "CirCor", "modality": "audio_heart", "source_id": patient, "description": "Heart sound PCG case"})
            tables["AUD_META"].append({
                "case_id": case_id, "audio_id": audio_id, "dataset": "CirCor", "modality": "heart",
                "file_name": wav.name, "file_path": str(wav), "patient_id": safe_id(patient), "recording_site": rec.get("site", ""),
                "samplerate": info.get("samplerate"), "channels": info.get("channels"), "duration_sec": info.get("duration_sec"),
                "murmur": meta.get("Murmur", ""), "outcome": meta.get("Outcome", ""), "age": meta.get("Age", ""), "sex": meta.get("Sex", ""), "source_info": dumps(meta),
            })
            tables["AUD_QLT"].append({"audio_id": audio_id, "segment_id": "", "quality_id": f"qlt_{audio_id}", "snr": "", "noise_level": q.get("quality_flag"), "clipping": bool(q.get("clipping_ratio") not in ["", None] and float(q.get("clipping_ratio", 0)) > 0.01), "artifacts": "[]", "usable": q.get("quality_flag") in ["usable", "not_calculated"], "extra": dumps(q)})
            for seg in read_circor_tsv(root / rec["tsv_file"]):
                seg_id = f"seg_{audio_id}_{seg['idx']:05d}"
                evt_id = f"evt_{audio_id}_{seg['idx']:05d}"
                tables["AUD_SEG"].append({"case_id": case_id, "audio_id": audio_id, "segment_id": seg_id, "time_start": seg["time_start"], "time_end": seg["time_end"], "segment_type": "heartbeat_state", "source": "CirCor TSV"})
                tables["AUD_EVT"].append({"case_id": case_id, "audio_event_id": evt_id, "audio_id": audio_id, "segment_id": seg_id, "time_start": seg["time_start"], "time_end": seg["time_end"], "event_type": seg["state_name"], "confidence": 1.0, "attributes": dumps({"state_id": seg["state_id"]})})
            if meta.get("Murmur"):
                tables["AUD_EVT"].append({"case_id": case_id, "audio_event_id": f"evt_{audio_id}_murmur_label", "audio_id": audio_id, "segment_id": "", "time_start": 0, "time_end": info.get("duration_sec", ""), "event_type": "murmur_" + safe_id(meta.get("Murmur")).lower(), "confidence": 1.0, "attributes": dumps({"source": "patient TXT metadata"})})
            n += 1
            if n % 250 == 0:
                log(f"[CirCor] records={n}")
    log(f"[CirCor] done records={n}")


def cycle_label(crackles: int, wheezes: int) -> str:
    if crackles == 0 and wheezes == 0:
        return "normal"
    if crackles == 1 and wheezes == 0:
        return "crackle"
    if crackles == 0 and wheezes == 1:
        return "wheeze"
    if crackles == 1 and wheezes == 1:
        return "both"
    return "unknown"


def read_icbhi_txt(path: Path) -> List[Dict[str, Any]]:
    out = []
    if not path.exists():
        return out
    for i, line in enumerate(path.read_text(encoding="utf-8", errors="ignore").splitlines()):
        parts = re.split(r"\s+", line.strip())
        if len(parts) < 4:
            continue
        try:
            c, w = int(float(parts[2])), int(float(parts[3]))
            out.append({"idx": i, "time_start": float(parts[0]), "time_end": float(parts[1]), "crackles": c, "wheezes": w, "cycle_label": cycle_label(c, w)})
        except Exception:
            pass
    return out


def build_icbhi_tables(tables: Dict[str, List[Dict[str, Any]]], root: Path, limit: int = 0, compute_quality: bool = False) -> None:
    if not root or not root.exists():
        log(f"[ICBHI] missing dir: {root}")
        return
    n = 0
    for wav in sorted(root.glob("*.wav")):
        if limit and n >= limit:
            log(f"[ICBHI] limit reached: {limit}")
            return
        ann = wav.with_suffix(".txt")
        if not ann.exists():
            continue
        patient = wav.stem.split("_")[0]
        case_id = f"case_icbhi_{safe_id(patient)}"
        audio_id = f"icbhi_{safe_id(wav.stem)}"
        info = sf_info(wav)
        q = audio_quality(wav, compute_quality)
        tables["CASE_META"].append({"case_id": case_id, "patient_pseudo_id": safe_id(patient), "encounter_id": "", "dataset": "ICBHI2017", "modality": "audio_lung", "source_id": patient, "description": "Respiratory sound case"})
        tables["AUD_META"].append({"case_id": case_id, "audio_id": audio_id, "dataset": "ICBHI2017", "modality": "lung", "file_name": wav.name, "file_path": str(wav), "patient_id": safe_id(patient), "recording_site": "", "samplerate": info.get("samplerate"), "channels": info.get("channels"), "duration_sec": info.get("duration_sec"), "murmur": "", "outcome": "", "age": "", "sex": "", "source_info": dumps({"txt_file": ann.name})})
        tables["AUD_QLT"].append({"audio_id": audio_id, "segment_id": "", "quality_id": f"qlt_{audio_id}", "snr": "", "noise_level": q.get("quality_flag"), "clipping": bool(q.get("clipping_ratio") not in ["", None] and float(q.get("clipping_ratio", 0)) > 0.01), "artifacts": "[]", "usable": q.get("quality_flag") in ["usable", "not_calculated"], "extra": dumps(q)})
        for row in read_icbhi_txt(ann):
            seg_id = f"seg_{audio_id}_{row['idx']:05d}"
            tables["AUD_SEG"].append({"case_id": case_id, "audio_id": audio_id, "segment_id": seg_id, "time_start": row["time_start"], "time_end": row["time_end"], "segment_type": "respiratory_cycle", "source": "ICBHI TXT"})
            tables["AUD_EVT"].append({"case_id": case_id, "audio_event_id": f"evt_{audio_id}_cycle_{row['idx']:05d}", "audio_id": audio_id, "segment_id": seg_id, "time_start": row["time_start"], "time_end": row["time_end"], "event_type": "respiratory_cycle", "confidence": 1.0, "attributes": dumps({"cycle_label": row["cycle_label"], "crackles": row["crackles"], "wheezes": row["wheezes"]})})
            if row["crackles"]:
                tables["AUD_EVT"].append({"case_id": case_id, "audio_event_id": f"evt_{audio_id}_crackle_{row['idx']:05d}", "audio_id": audio_id, "segment_id": seg_id, "time_start": row["time_start"], "time_end": row["time_end"], "event_type": "crackle", "confidence": 1.0, "attributes": dumps({"source": "ICBHI annotation"})})
            if row["wheezes"]:
                tables["AUD_EVT"].append({"case_id": case_id, "audio_event_id": f"evt_{audio_id}_wheeze_{row['idx']:05d}", "audio_id": audio_id, "segment_id": seg_id, "time_start": row["time_start"], "time_end": row["time_end"], "event_type": "wheeze", "confidence": 1.0, "attributes": dumps({"source": "ICBHI annotation"})})
        n += 1
        if n % 100 == 0:
            log(f"[ICBHI] records={n}")
    log(f"[ICBHI] done records={n}")



def _pil_from_any(x: Any):
    """Best-effort conversion of dataset image/mask values to PIL.Image."""
    from PIL import Image
    import numpy as np
    if x is None:
        return None
    if isinstance(x, Image.Image):
        return x
    if isinstance(x, dict):
        if "path" in x and x["path"]:
            return Image.open(x["path"])
        if "bytes" in x and x["bytes"]:
            from io import BytesIO
            return Image.open(BytesIO(x["bytes"]))
    if isinstance(x, (str, Path)) and Path(x).exists():
        return Image.open(x)
    try:
        arr = np.array(x)
        if arr.size:
            return Image.fromarray(arr.astype("uint8"))
    except Exception:
        pass
    return None


def _find_image_and_mask_columns(sample: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    image_col = None
    mask_col = None
    for k, v in sample.items():
        lk = str(k).lower()
        if image_col is None and any(x in lk for x in ["image", "img", "photo"]):
            if _pil_from_any(v) is not None:
                image_col = k
        if mask_col is None and any(x in lk for x in ["mask", "seg", "annotation", "label_map"]):
            if _pil_from_any(v) is not None:
                mask_col = k
    cols = [k for k, v in sample.items() if _pil_from_any(v) is not None]
    if image_col is None and cols:
        image_col = cols[0]
    if mask_col is None:
        for k in cols:
            if k != image_col:
                mask_col = k
                break
    return image_col, mask_col


def _approx_lung_roi_mask(img):
    """Approximate bilateral lung ROI mask for frontal chest X-ray.

    This is not a radiologist segmentation. It is a generated ROI mask used
    to satisfy the IMG_STRUCT layer for an image-classification dataset that
    has Normal/Pneumonia labels but no ground-truth masks.
    """
    from PIL import Image, ImageDraw, ImageFilter
    img_l = img.convert("L")
    w, h = img_l.size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    left_box = (int(0.14*w), int(0.17*h), int(0.49*w), int(0.88*h))
    right_box = (int(0.51*w), int(0.17*h), int(0.86*w), int(0.88*h))
    draw.ellipse(left_box, fill=255)
    draw.ellipse(right_box, fill=255)
    draw.rectangle((int(0.46*w), int(0.13*h), int(0.54*w), int(0.92*h)), fill=0)
    radius = max(1, int(min(w, h) * 0.006))
    mask = mask.filter(ImageFilter.GaussianBlur(radius=radius))
    mask = mask.point(lambda p: 255 if p > 40 else 0)
    return mask


def _pseudo_mask_from_image(img):
    """Fallback mask for image records: approximate lung fields."""
    return _approx_lung_roi_mask(img)


def _mask_stats(mask_img) -> Dict[str, Any]:
    import numpy as np
    arr = np.asarray(mask_img.convert("L"))
    m = arr > 0
    h, w = m.shape[:2]
    area = int(m.sum())
    if area == 0:
        return {"x": 0, "y": 0, "width": 0, "height": 0, "area_px": 0, "area_ratio": 0.0}
    ys, xs = np.where(m)
    x1, x2 = int(xs.min()), int(xs.max())
    y1, y2 = int(ys.min()), int(ys.max())
    return {"x": x1, "y": y1, "width": x2 - x1 + 1, "height": y2 - y1 + 1, "area_px": area, "area_ratio": float(area / max(1, w * h))}



def _make_mask_from_yolo_label(label_path: Path, size: Tuple[int, int]):
    """Create binary mask from YOLO bbox/segmentation txt annotation."""
    from PIL import Image, ImageDraw
    w, h = size
    mask = Image.new("L", (w, h), 0)
    draw = ImageDraw.Draw(mask)
    if not label_path or not label_path.exists():
        return None
    try:
        lines = [ln.strip() for ln in label_path.read_text(encoding="utf-8", errors="ignore").splitlines() if ln.strip()]
    except Exception:
        return None
    for ln in lines[:3]:
        parts = ln.split()
        if len(parts) < 5:
            continue
        try:
            nums = [float(x) for x in parts[1:]]
        except Exception:
            continue
        # YOLO bbox: class x_center y_center width height
        if len(nums) == 4:
            xc, yc, bw, bh = nums
            if max(nums) <= 1.5:
                xc, bw = xc * w, bw * w
                yc, bh = yc * h, bh * h
            x1, y1 = xc - bw / 2, yc - bh / 2
            x2, y2 = xc + bw / 2, yc + bh / 2
            draw.rectangle([x1, y1, x2, y2], fill=255)
        # YOLO segmentation: class x1 y1 x2 y2 ...
        elif len(nums) >= 6 and len(nums) % 2 == 0:
            pts = []
            norm = max(nums) <= 1.5
            for x, y in zip(nums[0::2], nums[1::2]):
                pts.append((x * w if norm else x, y * h if norm else y))
            if len(pts) >= 3:
                draw.polygon(pts, fill=255)
    return mask


def _find_local_image_label_pairs(root: Path, limit: int = 200) -> List[Tuple[Path, Optional[Path], Optional[Path]]]:
    """Find image files and optional YOLO label/mask files in an extracted dataset."""
    image_ext = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
    all_files = [p for p in root.rglob("*") if p.is_file()]
    mask_map: Dict[str, Path] = {}
    label_map: Dict[str, Path] = {}
    images: List[Path] = []
    for p in all_files:
        low = str(p).lower().replace("\\", "/")
        stem = p.stem.lower().replace("_mask", "").replace("-mask", "").replace("mask_", "").replace("mask-", "")
        if p.suffix.lower() == ".txt" and ("label" in low or "annotation" in low or "labels" in low):
            label_map[p.stem.lower()] = p
            continue
        if p.suffix.lower() in image_ext:
            if "mask" in low or "segmentation" in low:
                mask_map[stem] = p
            elif not any(x in low for x in ["/masks/", "/mask/", "/labels/", "/label/"]):
                images.append(p)
    images = sorted(images)[:limit if limit else None]
    pairs = []
    for img in images:
        stem = img.stem.lower()
        label = label_map.get(stem)
        # common YOLO layout: images/train/xxx.jpg -> labels/train/xxx.txt
        if label is None:
            candidates = list(root.rglob(img.stem + ".txt"))
            candidates = [c for c in candidates if "label" in str(c).lower() or "annotation" in str(c).lower()]
            label = candidates[0] if candidates else None
        mask = mask_map.get(stem)
        pairs.append((img, label, mask))
    return pairs


def _label_to_name(ds, label_value) -> str:
    """Convert HF ClassLabel/int label to readable string."""
    try:
        names = ds.features["label"].names
        return str(names[int(label_value)])
    except Exception:
        return str(label_value)


def _iter_hf_splits(dataset_name: str, split: str):
    """Yield (split_name, dataset) for HuggingFace image dataset."""
    from datasets import load_dataset
    if str(split).lower() in ["all", "*"]:
        dsd = load_dataset(dataset_name, cache_dir=str(HF_CACHE_DIR))
        for s in dsd.keys():
            yield s, dsd[s]
    else:
        try:
            yield split, load_dataset(dataset_name, split=split, cache_dir=str(HF_CACHE_DIR))
        except Exception:
            dsd = load_dataset(dataset_name, cache_dir=str(HF_CACHE_DIR))
            first = "train" if "train" in dsd else list(dsd.keys())[0]
            log(f"[IMG][WARN] split={split} not available, using {first}")
            yield first, dsd[first]


def build_image_tables(tables: Dict[str, List[Dict[str, Any]]], dataset_name: str = IMAGE_DATASET_DEFAULT, split: str = IMAGE_SPLIT_DEFAULT, limit: int = 200) -> None:
    """Create IMG_STRUCT / IMG_FINDING / IMG_ATTR from chest X-ray images.

    Default dataset: hf-vision/chest-xray-pneumonia. It has chest X-ray
    images and Normal/Pneumonia class labels. It does not provide real masks
    or bboxes, so IMG_STRUCT uses an approximate bilateral lung ROI mask
    generated from image dimensions. The class label becomes IMG_FINDING and
    IMG_ATTR severity.
    """
    out_img_dir = APP_DATA_DIR / "images"
    out_img_dir.mkdir(parents=True, exist_ok=True)
    n = 0
    try:
        log(f"[IMG] loading chest X-ray dataset: {dataset_name}, split={split}")
        for split_name, ds in _iter_hf_splits(dataset_name, split):
            for row in ds:
                if limit and n >= limit:
                    log(f"[IMG] limit reached: {limit}")
                    log(f"[IMG] done images={n}")
                    return
                img = None
                for key in ["image", "img", "jpg", "png"]:
                    if key in row:
                        img = _pil_from_any(row.get(key))
                        if img is not None:
                            break
                if img is None:
                    for v in row.values():
                        img = _pil_from_any(v)
                        if img is not None:
                            break
                if img is None:
                    continue
                label_raw = row.get("label", row.get("labels", row.get("class", "unknown")))
                label_name = _label_to_name(ds, label_raw)
                _append_chest_xray_annotation(tables, img, n, dataset_name, split_name, label_name, label_raw)
                n += 1
                if n % 50 == 0:
                    log(f"[IMG] images={n}")
        log(f"[IMG] done images={n}")
    except Exception as e:
        log(f"[IMG][WARN] cannot load chest X-ray dataset {dataset_name}: {e}")
        if not tables["IMG_STRUCT"]:
            log("[IMG][WARN] IMG_* will remain empty/placeholder")


def _append_chest_xray_annotation(tables: Dict[str, List[Dict[str, Any]]], img, i: int, dataset_name: str, split: str, label_name: str, label_raw: Any) -> None:
    """Append one CXR image with generated lung ROI mask and pneumonia finding."""
    img = img.convert("RGB")
    mask = _approx_lung_roi_mask(img).resize(img.size)
    image_id = f"img_cxr_{i:06d}"
    region_id = f"roi_{image_id}_bilateral_lung_fields"
    mask_id = f"mask_{image_id}_bilateral_lung_fields"
    finding_id = f"finding_{image_id}_pneumonia_label"
    case_id = f"case_cxr_{i:06d}"
    preview_img = img.copy(); preview_img.thumbnail((640, 640))
    preview_mask = mask.resize(preview_img.size)
    img_rel = f"images/{image_id}.png"
    mask_rel = f"images/{mask_id}.png"
    preview_img.save(APP_DATA_DIR / img_rel)
    preview_mask.save(APP_DATA_DIR / mask_rel)
    st = _mask_stats(mask)
    label_lower = str(label_name).lower()
    is_pneumonia = ("pneum" in label_lower) or str(label_raw).lower() in ["1", "pneumonia"]
    finding_type = "pneumonia" if is_pneumonia else "no_finding"
    finding_label = "PNEUMONIA" if is_pneumonia else "NORMAL"
    severity = "suspected_pneumonia" if is_pneumonia else "normal"
    tables["CASE_META"].append({"case_id": case_id, "patient_pseudo_id": "", "encounter_id": "", "dataset": "ChestXrayPneumoniaHF", "modality": "image_chest_xray", "source_id": str(i), "description": "Chest X-ray image with Normal/Pneumonia label and generated bilateral lung ROI mask"})
    tables["IMG_STRUCT"].append({"case_id": case_id, "image_id": image_id, "region_id": region_id, "mask_id": mask_id, "source_dataset": dataset_name, "split": split, "image_col": "image", "mask_col": "generated_bilateral_lung_roi", "modality": "chest_xray", "file_name": f"{image_id}.png", "preview_image": img_rel, "preview_mask": mask_rel, "width": img.size[0], "height": img.size[1], "roi_x": st["x"], "roi_y": st["y"], "roi_width": st["width"], "roi_height": st["height"], "mask_area_px": st["area_px"], "mask_area_ratio": st["area_ratio"], "annotation_format": "JSON/COCO-like bbox + generated binary lung ROI mask", "note": "Approximate bilateral lung ROI generated for classification dataset; not radiologist segmentation", "finding_id": finding_id})
    tables["IMG_FINDING"].append({"case_id": case_id, "image_id": image_id, "finding_id": finding_id, "region_id": region_id, "finding_type": finding_type, "finding_label": finding_label, "confidence": 1.0, "source": "image_folder_class_label"})
    tables["IMG_ATTR"].append({"finding_id": finding_id, "size": "bilateral_lung_roi", "laterality": "bilateral_unspecified", "severity": severity, "area_px": st["area_px"], "area_ratio": st["area_ratio"], "bbox": dumps({"x": st["x"], "y": st["y"], "width": st["width"], "height": st["height"]}), "label_raw": str(label_raw)})

def add_alignment(tables: Dict[str, List[Dict[str, Any]]], max_links: int = 2000) -> None:
    mentions = [m for m in tables["TXT_NER"] if "disease" in str(m.get("entity_type", "")).lower()]
    audio_events = [e for e in tables["AUD_EVT"] if e.get("event_type") in ["wheeze", "crackle"] or str(e.get("event_type", "")).startswith("murmur_")]
    image_regions = [r for r in tables["IMG_STRUCT"] if r.get("image_id") != "not_used"]
    n = 0
    audio_budget = max_links if not image_regions else max(1, max_links // 2)
    for m in mentions:
        if n >= audio_budget:
            break
        txt = str(m.get("text", "")).lower()
        candidates = audio_events
        if any(x in txt for x in ["asthma", "bronch", "pneum", "lung", "respir", "pulmonary"]):
            candidates = [e for e in audio_events if e.get("event_type") in ["wheeze", "crackle"]]
        if any(x in txt for x in ["heart", "cardiac", "murmur", "valve"]):
            candidates = [e for e in audio_events if str(e.get("event_type", "")).startswith("murmur_")]
        if candidates:
            e = candidates[n % len(candidates)]
            n += 1
            tables["MM_ALIGN"].append({"link_id": f"mm_audio_link_{n:05d}", "case_id": m.get("case_id", ""), "mention_id": m.get("mention_id", ""), "audio_event_id": e.get("audio_event_id", ""), "region_id": "", "finding_id": "", "alignment_type": "semantic_text_audio_alignment", "confidence": 0.55, "note": "semantic bridge across datasets, not same-patient alignment"})
    if image_regions and mentions:
        image_budget = max_links - n
        for i, m in enumerate(mentions[:image_budget]):
            r = image_regions[i % len(image_regions)]
            txt = str(m.get("text", "")).lower()
            score = 0.72 if any(x in txt for x in ["pneum", "lung", "pulmonary", "respir", "chest", "opacity", "infiltrat", "bronch"]) else 0.45
            n += 1
            tables["MM_ALIGN"].append({"link_id": f"mm_image_link_{n:05d}", "case_id": m.get("case_id", ""), "mention_id": m.get("mention_id", ""), "audio_event_id": "", "region_id": r.get("region_id", ""), "finding_id": r.get("finding_id", ""), "alignment_type": "semantic_text_image_alignment", "confidence": score, "note": "Disease mention is linked to chest X-ray lung ROI/finding on domain level; source datasets are not same-patient aligned"})

def add_agent_and_eval_layers(tables: Dict[str, List[Dict[str, Any]]]) -> None:
    if not tables["IMG_STRUCT"]:
        tables["IMG_STRUCT"].append({"case_id": "not_used", "image_id": "not_used", "region_id": "not_used", "mask_id": "", "note": "image modality was not loaded"})
        tables["IMG_FINDING"].append({"case_id": "not_used", "image_id": "not_used", "finding_id": "not_used", "region_id": "not_used", "finding_type": "not_used"})
        tables["IMG_ATTR"].append({"finding_id": "not_used", "size": "", "laterality": "", "severity": ""})
    tables["PRM_INPUT"].extend([
        {"run_id": "run_full_kg", "prompt_id": "prompt_text", "agent_id": "text_agent", "turn_id": "1", "prompt_text": "Extract text annotation layers from BC5CDR.", "context_ref": "BC5CDR"},
        {"run_id": "run_full_kg", "prompt_id": "prompt_audio", "agent_id": "audio_agent", "turn_id": "2", "prompt_text": "Extract audio segments and clinical audio events.", "context_ref": "CirCor + ICBHI"},
        {"run_id": "run_full_kg", "prompt_id": "prompt_kg", "agent_id": "kg_agent", "turn_id": "3", "prompt_text": "Build RDF graph and run SPARQL queries.", "context_ref": "all layers"},
    ])
    tables["PRM_TOOL"].extend([
        {"tool_call_id": "tool_1", "run_id": "run_full_kg", "turn_id": "1", "tool_name": "datasets.load_dataset", "tool_input": "bigbio/bc5cdr", "tool_output_summary": f"TXT_DOC={len(tables['TXT_DOC'])}, TXT_NER={len(tables['TXT_NER'])}"},
        {"tool_call_id": "tool_2", "run_id": "run_full_kg", "turn_id": "2", "tool_name": "audio parsers", "tool_input": "WAV + TSV/TXT", "tool_output_summary": f"AUD_META={len(tables['AUD_META'])}, AUD_EVT={len(tables['AUD_EVT'])}"},
        {"tool_call_id": "tool_3", "run_id": "run_full_kg", "turn_id": "3", "tool_name": "rdflib", "tool_input": "annotation tables", "tool_output_summary": "RDF + SPARQL"},
    ])
    tables["PRM_OUTPUT"].extend([
        {"response_id": "response_1", "agent_id": "text_agent", "turn_id": "1", "run_id": "run_full_kg", "response_text": f"Text layers created: mentions={len(tables['TXT_NER'])}, relations={len(tables['TXT_REL'])}."},
        {"response_id": "response_2", "agent_id": "audio_agent", "turn_id": "2", "run_id": "run_full_kg", "response_text": f"Audio layers created: records={len(tables['AUD_META'])}, events={len(tables['AUD_EVT'])}."},
        {"response_id": "response_3", "agent_id": "kg_agent", "turn_id": "3", "run_id": "run_full_kg", "response_text": f"MM links={len(tables['MM_ALIGN'])}; RDF graph is ready."},
    ])
    tables["RSN_GRAPH"].extend([
        {"claim_id": "claim_1", "evidence_id": "TXT_NER/TXT_REL", "decision_id": "use_bc5cdr_gold", "run_id": "run_full_kg", "claim_text": "BC5CDR provides gold biomedical NER, normalization and CID relations.", "decision": "accepted"},
        {"claim_id": "claim_2", "evidence_id": "AUD_SEG/AUD_EVT", "decision_id": "use_audio_annotations", "run_id": "run_full_kg", "claim_text": "CirCor and ICBHI provide temporal audio annotations.", "decision": "accepted"},
        {"claim_id": "claim_3", "evidence_id": "MM_ALIGN", "decision_id": "semantic_bridge", "run_id": "run_full_kg", "claim_text": "Text and audio layers can be integrated by semantic links.", "decision": "accepted_with_note"},
    ])
    tables["EVAL_LAYER"].extend([
        {"run_id": "run_full_kg", "metric_id": "m_text_mentions", "metric_name": "text_mentions", "value": len(tables["TXT_NER"]), "unit": "rows"},
        {"run_id": "run_full_kg", "metric_id": "m_audio_events", "metric_name": "audio_events", "value": len(tables["AUD_EVT"]), "unit": "rows"},
        {"run_id": "run_full_kg", "metric_id": "m_mm_links", "metric_name": "mm_links", "value": len(tables["MM_ALIGN"]), "unit": "rows"},
        {"run_id": "run_full_kg", "metric_id": "m_tables", "metric_name": "non_empty_tables", "value": sum(1 for x in TABLES if tables[x]), "unit": "tables"},
    ])


def deduplicate_cases(tables: Dict[str, List[Dict[str, Any]]]) -> None:
    seen, out = set(), []
    for r in tables["CASE_META"]:
        key = (r.get("case_id"), r.get("dataset"), r.get("modality"))
        if key not in seen:
            seen.add(key)
            out.append(r)
    tables["CASE_META"] = out


def add_stats(tables: Dict[str, List[Dict[str, Any]]]) -> None:
    tables["DATASET_STATS"].clear()
    for name in TABLES:
        if name != "DATASET_STATS":
            tables["DATASET_STATS"].append({"dataset": "generated_tables", "stat_name": f"{name}_rows", "stat_value": len(tables[name]), "description": f"Rows in {name}"})
    for dataset, stat, val, descr in [
        ("BC5CDR", "source_articles", 1500, "BC5CDR source corpus articles"),
        ("ICBHI2017", "source_recordings", 920, "ICBHI annotated respiratory recordings"),
        ("ICBHI2017", "source_subjects", 126, "ICBHI subjects"),
        ("ICBHI2017", "source_resp_cycles", 6898, "ICBHI respiratory cycles"),
    ]:
        tables["DATASET_STATS"].append({"dataset": dataset, "stat_name": stat, "stat_value": val, "description": descr})


def fields(rows: List[Dict[str, Any]]) -> List[str]:
    out, seen = [], set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                seen.add(k)
                out.append(k)
    return out


def export_tables(tables: Dict[str, List[Dict[str, Any]]]) -> None:
    all_annotations = {}
    for name in TABLES:
        rows = tables[name]
        all_annotations[name] = rows
        fs = fields(rows)
        with (EXPORT_DIR / "csv" / f"{name}.csv").open("w", encoding="utf-8-sig", newline="") as f:
            if fs:
                w = csv.DictWriter(f, fieldnames=fs, extrasaction="ignore")
                w.writeheader()
                w.writerows(rows)
        (EXPORT_DIR / "json" / f"{name}.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    (EXPORT_DIR / "json" / "all_annotations.json").write_text(json.dumps(all_annotations, ensure_ascii=False, indent=2), encoding="utf-8")
    root = Element("annotations")
    for name in TABLES:
        table_el = SubElement(root, "table", name=name)
        for row in tables[name]:
            row_el = SubElement(table_el, "row")
            for k, v in row.items():
                cell = SubElement(row_el, safe_id(k))
                cell.text = "" if v is None else str(v)
    ElementTree(root).write(EXPORT_DIR / "xml" / "annotations.xml", encoding="utf-8", xml_declaration=True)


def build_rdf(tables: Dict[str, List[Dict[str, Any]]], include_tokens: bool = False):
    from rdflib import Graph, Literal, Namespace, RDF, RDFS
    from rdflib.namespace import XSD

    g = Graph()
    EX = Namespace(EX_BASE)
    SCHEMA = Namespace("https://schema.org/")
    g.bind("ex", EX); g.bind("schema", SCHEMA); g.bind("rdf", RDF); g.bind("rdfs", RDFS)

    def U(kind: str, value: Any):
        return EX[f"{kind}/{urllib.parse.quote(safe_id(value), safe='')}"]

    def L(value: Any):
        if isinstance(value, bool):
            return Literal(value, datatype=XSD.boolean)
        if isinstance(value, int):
            return Literal(value, datatype=XSD.integer)
        if isinstance(value, float):
            return Literal(value, datatype=XSD.double)
        return Literal("" if value is None else str(value))

    def add_literals(subj, row, skip=()):
        for k, v in row.items():
            if k not in skip:
                g.add((subj, EX[safe_id(k)], L(v)))

    for cls in ["Case","TextDocument","Token","Mention","Concept","TextRelation","AudioRecord","AudioSegment","AudioEvent","QualityAnnotation","ImageRecord","ImageRegion","ImageMask","ImageFinding","ImageAttribute","MultimodalAlignment","Prompt","ToolCall","AgentOutput","ReasoningClaim","EvaluationMetric","DatasetStat"]:
        g.add((EX[cls], RDF.type, RDFS.Class))

    for r in tables["CASE_META"]:
        s = U("case", r["case_id"]); g.add((s, RDF.type, EX.Case)); add_literals(s, r)
    for r in tables["TXT_DOC"]:
        s = U("text_document", r["doc_id"]); g.add((s, RDF.type, EX.TextDocument)); g.add((s, SCHEMA.text, L(r.get("text","")))); add_literals(s, r, ("text",)); g.add((U("case", r["case_id"]), EX.hasTextDocument, s))
    if include_tokens:
        lemma = {r["token_id"]: r for r in tables["TXT_LEMMA"] if r.get("token_id")}
        pos = {r["token_id"]: r for r in tables["TXT_POS"] if r.get("token_id")}
        dep = {r["token_id"]: r for r in tables["TXT_DEP"] if r.get("token_id")}
        for r in tables["TXT_SEG"]:
            s = U("token", r["token_id"]); g.add((s, RDF.type, EX.Token)); add_literals(s, r); g.add((U("text_document", r["doc_id"]), EX.hasToken, s))
            if r["token_id"] in lemma: g.add((s, EX.lemma, L(lemma[r["token_id"]].get("lemma",""))))
            if r["token_id"] in pos:
                g.add((s, EX.upos, L(pos[r["token_id"]].get("upos","")))); g.add((s, EX.xpos, L(pos[r["token_id"]].get("xpos",""))))
            if r["token_id"] in dep:
                g.add((s, EX.dep, L(dep[r["token_id"]].get("dep",""))))
                if dep[r["token_id"]].get("head_id"): g.add((s, EX.dependsOn, U("token", dep[r["token_id"]]["head_id"])))
    norms = defaultdict(list)
    for r in tables["TXT_NORM"]:
        norms[r.get("mention_id")].append(r)
    for r in tables["TXT_NER"]:
        s = U("mention", r["mention_id"]); g.add((s, RDF.type, EX.Mention)); g.add((s, RDFS.label, L(r.get("text","")))); add_literals(s, r)
        g.add((U("text_document", r["doc_id"]), EX.hasMention, s)); g.add((U("case", r["case_id"]), EX.hasMention, s))
        for n in norms.get(r["mention_id"], []):
            c = U("concept", n.get("concept_id") or r["mention_id"]); g.add((c, RDF.type, EX.Concept)); add_literals(c, n, ("mention_id",)); g.add((s, EX.normalizedTo, c))
    for r in tables["TXT_REL"]:
        s = U("text_relation", r["relation_id"]); g.add((s, RDF.type, EX.TextRelation)); add_literals(s, r)
        g.add((s, EX.relationSource, U("mention", r["mention_id_src"]))); g.add((s, EX.relationTarget, U("mention", r["mention_id_tgt"])))
    for r in tables["AUD_META"]:
        s = U("audio", r["audio_id"]); g.add((s, RDF.type, EX.AudioRecord)); add_literals(s, r); g.add((U("case", r["case_id"]), EX.hasAudioRecord, s))
    for r in tables["AUD_SEG"]:
        s = U("audio_segment", r["segment_id"]); g.add((s, RDF.type, EX.AudioSegment)); add_literals(s, r); g.add((U("audio", r["audio_id"]), EX.hasAudioSegment, s))
    for r in tables["AUD_EVT"]:
        s = U("audio_event", r["audio_event_id"]); g.add((s, RDF.type, EX.AudioEvent)); add_literals(s, r); g.add((U("audio", r["audio_id"]), EX.hasAudioEvent, s))
        if r.get("segment_id"): g.add((U("audio_segment", r["segment_id"]), EX.hasAudioEvent, s))
    for r in tables["AUD_QLT"]:
        s = U("quality", r["quality_id"]); g.add((s, RDF.type, EX.QualityAnnotation)); add_literals(s, r); g.add((U("audio", r["audio_id"]), EX.hasQualityAnnotation, s))
    for r in tables["IMG_STRUCT"]:
        if r.get("image_id") == "not_used":
            continue
        img = U("image", r["image_id"]); region = U("image_region", r["region_id"]); mask = U("image_mask", r.get("mask_id", r["region_id"]))
        g.add((img, RDF.type, EX.ImageRecord)); add_literals(img, r, ("region_id", "mask_id", "finding_id")); g.add((U("case", r["case_id"]), EX.hasImageRecord, img))
        g.add((region, RDF.type, EX.ImageRegion)); add_literals(region, r, ("image_id",)); g.add((img, EX.hasImageRegion, region))
        if r.get("mask_id"):
            g.add((mask, RDF.type, EX.ImageMask)); g.add((region, EX.hasMask, mask)); g.add((mask, EX.mask_id, L(r.get("mask_id"))))
    for r in tables["IMG_FINDING"]:
        if r.get("finding_id") == "not_used":
            continue
        finding = U("image_finding", r["finding_id"]); g.add((finding, RDF.type, EX.ImageFinding)); add_literals(finding, r)
        if r.get("region_id"):
            g.add((U("image_region", r["region_id"]), EX.hasFinding, finding))
    for r in tables["IMG_ATTR"]:
        if r.get("finding_id") == "not_used":
            continue
        attr = U("image_attribute", r["finding_id"]); g.add((attr, RDF.type, EX.ImageAttribute)); add_literals(attr, r)
        g.add((U("image_finding", r["finding_id"]), EX.hasAttribute, attr))
    for r in tables["MM_ALIGN"]:
        s = U("alignment", r["link_id"]); g.add((s, RDF.type, EX.MultimodalAlignment)); add_literals(s, r)
        if r.get("mention_id"): g.add((s, EX.linksMention, U("mention", r["mention_id"])))
        if r.get("audio_event_id"): g.add((s, EX.linksAudioEvent, U("audio_event", r["audio_event_id"])))
        if r.get("region_id"): g.add((s, EX.linksImageRegion, U("image_region", r["region_id"])))
        if r.get("finding_id"): g.add((s, EX.linksImageFinding, U("image_finding", r["finding_id"])))
    for table, cls, key, kind in [
        ("PRM_INPUT","Prompt","prompt_id","prompt"), ("PRM_TOOL","ToolCall","tool_call_id","tool_call"),
        ("PRM_OUTPUT","AgentOutput","response_id","agent_output"), ("RSN_GRAPH","ReasoningClaim","claim_id","reasoning"),
        ("EVAL_LAYER","EvaluationMetric","metric_id","metric"), ("DATASET_STATS","DatasetStat","stat_name","stat"),
    ]:
        for r in tables[table]:
            s = U(kind, r.get(key, len(g))); g.add((s, RDF.type, EX[cls])); add_literals(s, r)
    return g


PREFIX = "PREFIX ex: <" + EX_BASE + ">\\nPREFIX schema: <https://schema.org/>\\nPREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\\nPREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\\n"
QUERIES = {
    "q01_case_counts": "SELECT ?dataset ?modality (COUNT(DISTINCT ?case) AS ?cases) WHERE { ?case a ex:Case ; ex:dataset ?dataset ; ex:modality ?modality . } GROUP BY ?dataset ?modality ORDER BY ?dataset ?modality",
    "q02_text_documents_sample": "SELECT ?doc_id ?split ?source_doc_id ?text WHERE { ?doc a ex:TextDocument ; ex:doc_id ?doc_id ; ex:split ?split ; ex:source_doc_id ?source_doc_id ; schema:text ?text . } LIMIT 20",
    "q03_mentions_with_normalization": "SELECT ?mention_id ?mention_text ?entity_type ?kb ?concept WHERE { ?m a ex:Mention ; ex:mention_id ?mention_id ; ex:text ?mention_text ; ex:entity_type ?entity_type . OPTIONAL { ?m ex:normalizedTo ?c . OPTIONAL { ?c ex:kb_name ?kb . } OPTIONAL { ?c ex:concept_id ?concept . } } } LIMIT 100",
    "q04_chemical_disease_relations": "SELECT ?relation_id ?relation_type ?src_text ?tgt_text WHERE { ?rel a ex:TextRelation ; ex:relation_id ?relation_id ; ex:relation_type ?relation_type ; ex:relationSource ?src ; ex:relationTarget ?tgt . ?src ex:text ?src_text . ?tgt ex:text ?tgt_text . } LIMIT 100",
    "q05_audio_records_by_dataset": "SELECT ?dataset ?modality (COUNT(DISTINCT ?audio) AS ?audio_records) WHERE { ?audio a ex:AudioRecord ; ex:dataset ?dataset ; ex:modality ?modality . } GROUP BY ?dataset ?modality ORDER BY ?dataset ?modality",
    "q06_audio_event_counts": "SELECT ?event_type (COUNT(?event) AS ?count) WHERE { ?event a ex:AudioEvent ; ex:event_type ?event_type . } GROUP BY ?event_type ORDER BY DESC(?count)",
    "q07_pathological_audio_events": "SELECT ?audio_id ?event_type ?time_start ?time_end WHERE { ?event a ex:AudioEvent ; ex:audio_id ?audio_id ; ex:event_type ?event_type ; ex:time_start ?time_start ; ex:time_end ?time_end . FILTER(?event_type IN (\\\"wheeze\\\", \\\"crackle\\\", \\\"murmur_present\\\", \\\"murmur_unknown\\\")) } LIMIT 100",
    "q08_cross_modal_alignment": "SELECT ?link_id ?mention_text ?entity_type ?audio_event_type ?confidence WHERE { ?link a ex:MultimodalAlignment ; ex:link_id ?link_id ; ex:confidence ?confidence ; ex:linksMention ?m ; ex:linksAudioEvent ?e . ?m ex:text ?mention_text ; ex:entity_type ?entity_type . ?e ex:event_type ?audio_event_type . } LIMIT 100",
    "q09_dataset_stats": "SELECT ?dataset ?stat_name ?stat_value ?description WHERE { ?s a ex:DatasetStat ; ex:dataset ?dataset ; ex:stat_name ?stat_name ; ex:stat_value ?stat_value ; ex:description ?description . } ORDER BY ?dataset ?stat_name",
    "q10_agent_trace": "SELECT ?agent_id ?prompt ?response WHERE { ?p a ex:Prompt ; ex:agent_id ?agent_id ; ex:prompt_text ?prompt . OPTIONAL { ?o a ex:AgentOutput ; ex:agent_id ?agent_id ; ex:response_text ?response . } } ORDER BY ?agent_id",
    "q11_simple_all_types": "SELECT ?s ?type WHERE { ?s rdf:type ?type . } LIMIT 50",
    "q12_simple_audio_files": "SELECT ?audio_id ?dataset ?file_name ?duration WHERE { ?a a ex:AudioRecord ; ex:audio_id ?audio_id ; ex:dataset ?dataset ; ex:file_name ?file_name . OPTIONAL { ?a ex:duration_sec ?duration . } } LIMIT 50",
    "q13_image_findings": "SELECT ?image_id ?region_id ?finding_type ?confidence WHERE { ?f a ex:ImageFinding ; ex:image_id ?image_id ; ex:region_id ?region_id ; ex:finding_type ?finding_type . OPTIONAL { ?f ex:confidence ?confidence . } } LIMIT 100",
    "q14_image_roi_attributes": "SELECT ?finding_id ?size ?severity ?area_ratio ?bbox WHERE { ?a a ex:ImageAttribute ; ex:finding_id ?finding_id ; ex:size ?size ; ex:severity ?severity . OPTIONAL { ?a ex:area_ratio ?area_ratio . } OPTIONAL { ?a ex:bbox ?bbox . } } LIMIT 100",
    "q15_text_image_alignment": "SELECT ?link_id ?mention_text ?entity_type ?region_id ?finding_id ?confidence WHERE { ?link a ex:MultimodalAlignment ; ex:link_id ?link_id ; ex:linksMention ?m ; ex:linksImageRegion ?region ; ex:confidence ?confidence . ?m ex:text ?mention_text ; ex:entity_type ?entity_type . ?region ex:region_id ?region_id . OPTIONAL { ?link ex:finding_id ?finding_id . } } LIMIT 100",
}



def export_rdf_and_sparql(g, export_jsonld: bool = False):
    g.serialize(destination=str(EXPORT_DIR / "rdf" / "medical_kg.ttl"), format="turtle")
    g.serialize(destination=str(EXPORT_DIR / "rdf" / "medical_kg.nt"), format="nt")
    if export_jsonld:
        try:
            g.serialize(destination=str(EXPORT_DIR / "rdf" / "medical_kg.jsonld"), format="json-ld", indent=2)
        except MemoryError:
            (EXPORT_DIR / "rdf" / "medical_kg_jsonld_skipped.txt").write_text(
                "JSON-LD export was skipped: the graph is too large for rdflib JSON-LD serializer in memory. Use TTL or NT.",
                encoding="utf-8",
            )
    else:
        (EXPORT_DIR / "rdf" / "medical_kg_jsonld_skipped.txt").write_text(
            "JSON-LD export skipped by default to avoid MemoryError on large graphs. Use --export-jsonld only for small runs.",
            encoding="utf-8",
        )
    all_results = {}
    for name, query_body in QUERIES.items():
        query = (PREFIX + "\n" + query_body).replace("\\n", "\n").lstrip("\ufeff").strip()
        (EXPORT_DIR / "sparql" / f"{name}.rq").write_text(query, encoding="utf-8")
        try:
            result = g.query(query)
            vars_ = [str(v) for v in result.vars]
            rows = [{var: "" if val is None else str(val) for var, val in zip(vars_, row)} for row in result]
        except Exception as e:
            vars_ = ["error"]
            rows = [{"error": str(e)}]
        with (EXPORT_DIR / "sparql" / f"{name}_result.csv").open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=vars_)
            writer.writeheader()
            writer.writerows(rows)
        all_results[name] = rows
        log(f"[sparql] {name}: {len(rows)} rows")
    (EXPORT_DIR / "sparql" / "all_sparql_results.json").write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
    return all_results

def graph_sample(tables: Dict[str, List[Dict[str, Any]]], max_nodes: int = 180) -> Dict[str, Any]:
    nodes, edges = {}, []
    def add_node(node_id: str, label: str, group: str) -> None:
        if node_id in nodes or len(nodes) >= max_nodes:
            return
        angle = len(nodes) * 2 * math.pi / max_nodes
        radius = 180 + (len(nodes) % 8) * 25
        nodes[node_id] = {"id": node_id, "label": str(label)[:44], "group": group, "x": 450 + radius * math.cos(angle), "y": 340 + radius * math.sin(angle)}
    def add_edge(a: str, b: str, label: str) -> None:
        if a in nodes and b in nodes:
            edges.append({"source": a, "target": b, "label": label})
    for r in tables["CASE_META"][:20]:
        add_node("case:" + r["case_id"], r["case_id"], "case")
    for r in tables["TXT_DOC"][:25]:
        add_node("doc:" + r["doc_id"], r["doc_id"], "doc"); add_edge("case:" + r["case_id"], "doc:" + r["doc_id"], "hasText")
    for r in tables["TXT_NER"][:50]:
        add_node("mention:" + r["mention_id"], r["text"], "mention"); add_edge("doc:" + r["doc_id"], "mention:" + r["mention_id"], "hasMention")
    for r in tables["AUD_META"][:25]:
        add_node("audio:" + r["audio_id"], r["file_name"], "audio"); add_edge("case:" + r["case_id"], "audio:" + r["audio_id"], "hasAudio")
    for r in tables["AUD_EVT"][:50]:
        add_node("event:" + r["audio_event_id"], r["event_type"], "event"); add_edge("audio:" + r["audio_id"], "event:" + r["audio_event_id"], "hasEvent")
    for r in tables["IMG_STRUCT"][:25]:
        if r.get("image_id") == "not_used":
            continue
        add_node("image:" + r["image_id"], r["image_id"], "image"); add_edge("case:" + r["case_id"], "image:" + r["image_id"], "hasImage")
        add_node("region:" + r["region_id"], "ROI " + str(r.get("mask_area_ratio", ""))[:6], "region"); add_edge("image:" + r["image_id"], "region:" + r["region_id"], "hasROI")
    for r in tables["IMG_FINDING"][:25]:
        if r.get("finding_id") == "not_used":
            continue
        add_node("finding:" + r["finding_id"], r.get("finding_type", "finding"), "finding"); add_edge("region:" + r["region_id"], "finding:" + r["finding_id"], "finding")
    for r in tables["MM_ALIGN"][:30]:
        add_node("align:" + r["link_id"], r["alignment_type"], "align")
        add_edge("mention:" + r["mention_id"], "align:" + r["link_id"], "align")
        add_edge("align:" + r["link_id"], "event:" + r.get("audio_event_id", ""), "event")
        add_edge("align:" + r["link_id"], "region:" + r.get("region_id", ""), "imageROI")
    return {"nodes": list(nodes.values()), "edges": edges}


DASHBOARD_HTML = """<!doctype html>
<html lang="ru">
<head>
<meta charset="utf-8"><title>Medical KG Dashboard</title><meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#0b1220;--card:#111a2f;--line:#263853;--txt:#edf2ff;--mut:#9fb0d0;--acc:#1fd1c5;--gold:#ffd166}
*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;background:radial-gradient(circle at 20% 0%,#073b4c 0,var(--bg) 40%);color:var(--txt)}
header{padding:28px 36px;border-bottom:1px solid var(--line);position:sticky;top:0;background:rgba(11,18,32,.92);z-index:2}h1{margin:0}.sub{color:var(--mut);margin-top:8px}
nav{display:flex;gap:8px;flex-wrap:wrap;padding:14px 36px;border-bottom:1px solid var(--line)}button,input,select{border:1px solid var(--line);background:#0e1728;color:var(--txt);border-radius:12px;padding:10px 12px}button.active{background:var(--acc);color:#001316;font-weight:700}
main{padding:24px 36px 60px}.tab{display:none}.tab.active{display:block}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:14px}.card{background:rgba(17,26,47,.92);border:1px solid var(--line);border-radius:18px;padding:16px}.num{font-size:28px;font-weight:800;color:var(--acc)}.muted{color:var(--mut)}
.toolbar{display:flex;gap:10px;flex-wrap:wrap;margin-bottom:14px}.wrap{max-height:660px;overflow:auto;border:1px solid var(--line);border-radius:16px}table{width:100%;border-collapse:collapse;font-size:13px}th,td{border-bottom:1px solid var(--line);padding:8px;vertical-align:top}th{position:sticky;top:0;background:#10182a;color:var(--gold);text-align:left}.textcell{max-width:780px;white-space:pre-wrap;line-height:1.35}
#graphCanvas{width:100%;height:660px;background:#06101f;border:1px solid var(--line);border-radius:18px;display:block}pre{background:#080d18;border:1px solid var(--line);border-radius:14px;padding:14px;overflow:auto}
</style>
</head>
<body>
<header><h1>Мультимодальный медицинский RDF/KG</h1><div class="sub">Разметка текста + аудио, RDF через rdflib, SPARQL SELECT и dashboard</div></header>
<nav><button class="tabbtn active" data-tab="overview">Обзор</button><button class="tabbtn" data-tab="source">Исходные данные</button><button class="tabbtn" data-tab="ann">Аннотации</button><button class="tabbtn" data-tab="graph">Граф с zoom</button><button class="tabbtn" data-tab="sparql">SPARQL</button></nav>
<main>
<section id="overview" class="tab active"><div id="cards" class="grid"></div></section>
<section id="source" class="tab"><div class="toolbar"><input id="sourceQ" placeholder="поиск..." style="min-width:320px"><select id="sourceType"><option value="text">Тексты</option><option value="audio">Аудио</option><option value="image">Изображения</option></select></div><div class="wrap"><table id="sourceTable"></table></div></section>
<section id="ann" class="tab"><div class="toolbar"><input id="annQ" placeholder="поиск..." style="min-width:320px"><select id="annType"><option value="mentions">TXT_NER</option><option value="events">AUD_EVT</option><option value="align">MM_ALIGN</option><option value="imgfind">IMG_FINDING</option><option value="imgattr">IMG_ATTR</option></select></div><div class="wrap"><table id="annTable"></table></div></section>
<section id="graph" class="tab"><div class="toolbar"><input id="graphQ" placeholder="найти узел"><button id="zin">+</button><button id="zout">−</button><button id="zreset">Reset</button><span class="muted">колесико = zoom, мышь = движение</span></div><canvas id="graphCanvas" width="1400" height="760"></canvas></section>
<section id="sparql" class="tab"><div class="toolbar"><select id="sparqlSel"></select></div><pre id="sparqlName"></pre><div class="wrap"><table id="sparqlTable"></table></div></section>
</main>
<script>
const $=id=>document.getElementById(id);let D={},G,scale=1,ox=0,oy=0,drag=false,last=null,hi="";
async function j(n){let r=await fetch("data/"+n); if(!r.ok) throw new Error("Запусти: python -m http.server 8000 -d app"); return await r.json()}
function e(s){return String(s??"").replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
function filt(rows,q){q=String(q||"").toLowerCase();return q?rows.filter(r=>JSON.stringify(r).toLowerCase().includes(q)):rows}
function table(el,rows){rows=rows||[]; if(!rows.length){el.innerHTML="<tr><td>нет данных</td></tr>";return} let cols=Object.keys(rows[0]); el.innerHTML="<thead><tr>"+cols.map(c=>"<th>"+e(c)+"</th>").join("")+"</tr></thead><tbody>"+rows.slice(0,500).map(r=>"<tr>"+cols.map(c=>{let v=r[c]??""; if(c=="file_name"&&String(v).endsWith(".wav")) return `<td>${e(v)}<br><audio controls src="data/audio/${e(v)}"></audio></td>`;
let cv=String(v); if((c=="preview_image"||c=="preview_mask")&&cv) return `<td><img src="data/${e(cv)}" style="max-width:160px;border-radius:10px;border:1px solid var(--line)"></td>`; return `<td class="${String(v).length>120?'textcell':''}">${e(v)}</td>`}).join("")+"</tr>").join("")+"</tbody>"}
function cards(){let s=D.summary.table_sizes; let keys=["DATASET_STATS","CASE_META","TXT_DOC","TXT_SEG","TXT_NER","TXT_REL","AUD_META","AUD_SEG","AUD_EVT","IMG_STRUCT","IMG_FINDING","IMG_ATTR","MM_ALIGN","PRM_INPUT","RSN_GRAPH","EVAL_LAYER"]; $("cards").innerHTML=keys.map(k=>`<div class=card><div class=muted>${k}</div><div class=num>${s[k]||0}</div><div class=muted>rows</div></div>`).join("")}
function source(){let t=$("sourceType").value; table($("sourceTable"),filt(t=="text"?D.text:t=="audio"?D.audio:D.images,$("sourceQ").value))}
function ann(){let t=$("annType").value; let r=t=="mentions"?D.mentions:t=="events"?D.events:t=="align"?D.align:t=="imgfind"?D.imgfind:D.imgattr; table($("annTable"),filt(r,$("annQ").value))}
function sparql(){let k=$("sparqlSel").value;$("sparqlName").textContent=k;table($("sparqlTable"),D.sparql[k]||[])}
function color(g){return {case:"#ffd166",doc:"#8ecae6",mention:"#ffb703",audio:"#1fd1c5",event:"#f72585",image:"#70e000",region:"#38b000",finding:"#ccff33",align:"#c77dff"}[g]||"#aaa"}
function draw(){let c=$("graphCanvas"),ctx=c.getContext("2d");ctx.clearRect(0,0,c.width,c.height);ctx.save();ctx.translate(ox,oy);ctx.scale(scale,scale);let nodes=G.nodes||[],by=Object.fromEntries(nodes.map(n=>[n.id,n]));ctx.strokeStyle="rgba(160,180,220,.32)";ctx.lineWidth=1/scale;(G.edges||[]).forEach(ed=>{let a=by[ed.source],b=by[ed.target];if(a&&b){ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()}});nodes.forEach(n=>{let H=hi&&(n.label.toLowerCase().includes(hi)||n.id.toLowerCase().includes(hi));ctx.beginPath();ctx.arc(n.x,n.y,H?10:6,0,Math.PI*2);ctx.fillStyle=H?"#fff":color(n.group);ctx.fill();ctx.font=(H?15:11)+"px Arial";ctx.fillStyle=H?"#fff":"#d8e2ff";ctx.fillText(n.label,n.x+9,n.y+4)});ctx.restore()}
function initGraph(){G=D.graph;let c=$("graphCanvas");c.onwheel=ev=>{ev.preventDefault();scale*=ev.deltaY<0?1.12:.89;draw()};c.onmousedown=ev=>{drag=true;last={x:ev.clientX,y:ev.clientY}};window.onmouseup=()=>drag=false;window.onmousemove=ev=>{if(!drag)return;ox+=ev.clientX-last.x;oy+=ev.clientY-last.y;last={x:ev.clientX,y:ev.clientY};draw()};$("zin").onclick=()=>{scale*=1.2;draw()};$("zout").onclick=()=>{scale/=1.2;draw()};$("zreset").onclick=()=>{scale=1;ox=0;oy=0;draw()};$("graphQ").oninput=()=>{hi=$("graphQ").value.toLowerCase();draw()};draw()}
async function init(){D.summary=await j("summary.json");D.text=await j("text_docs_sample.json");D.mentions=await j("mentions_sample.json");D.audio=await j("audio_meta_sample.json");D.events=await j("audio_events_sample.json");D.images=await j("image_struct_sample.json");D.imgfind=await j("image_findings_sample.json");D.imgattr=await j("image_attrs_sample.json");D.align=await j("mm_align_sample.json");D.sparql=await j("sparql_results.json");D.graph=await j("graph_sample.json");document.querySelectorAll(".tabbtn").forEach(b=>b.onclick=()=>{document.querySelectorAll(".tabbtn").forEach(x=>x.classList.remove("active"));document.querySelectorAll(".tab").forEach(x=>x.classList.remove("active"));b.classList.add("active");$(b.dataset.tab).classList.add("active");if(b.dataset.tab=="graph")setTimeout(draw,50)});cards();source();ann();$("sourceQ").oninput=source;$("sourceType").onchange=source;$("annQ").oninput=ann;$("annType").onchange=ann;let ks=Object.keys(D.sparql);$("sparqlSel").innerHTML=ks.map(k=>`<option>${e(k)}</option>`).join("");$("sparqlSel").onchange=sparql;sparql();initGraph()}
init().catch(err=>document.body.innerHTML="<pre style='padding:30px;color:white'>"+e(err.message)+"</pre>")
</script></body></html>"""


def generate_dashboard(tables: Dict[str, List[Dict[str, Any]]], sparql: Dict[str, Any], copy_audio: int = 0) -> None:
    if copy_audio:
        copied = 0
        for r in tables["AUD_META"]:
            p = Path(str(r.get("file_path", "")))
            if p.exists() and p.suffix.lower() == ".wav":
                dst = APP_DATA_DIR / "audio" / p.name
                if not dst.exists():
                    shutil.copy2(p, dst)
                    copied += 1
                if copied >= copy_audio:
                    break
        log(f"[dashboard] copied audio={copied}")
    data = {
        "summary.json": {"table_sizes": {k: len(tables[k]) for k in TABLES}},
        "text_docs_sample.json": tables["TXT_DOC"][:200],
        "mentions_sample.json": tables["TXT_NER"][:500],
        "audio_meta_sample.json": tables["AUD_META"][:200],
        "audio_events_sample.json": tables["AUD_EVT"][:500],
        "image_struct_sample.json": tables["IMG_STRUCT"][:300],
        "image_findings_sample.json": tables["IMG_FINDING"][:300],
        "image_attrs_sample.json": tables["IMG_ATTR"][:300],
        "mm_align_sample.json": tables["MM_ALIGN"][:300],
        "sparql_results.json": sparql,
        "graph_sample.json": graph_sample(tables),
    }
    for name, obj in data.items():
        (APP_DATA_DIR / name).write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    (APP_DIR / "index.html").write_text(DASHBOARD_HTML, encoding="utf-8")


def write_select_examples() -> None:
    text = (
        "# -*- coding: utf-8 -*-\\n"
        "from rdflib import Graph\\n"
        "g = Graph()\\n"
        "g.parse('exports/rdf/medical_kg.ttl', format='turtle')\\n\\n"
        "queries = {\\n"
        "  'all_cases': 'PREFIX ex: <" + EX_BASE + "> SELECT ?case ?dataset ?modality WHERE { ?case a ex:Case ; ex:dataset ?dataset ; ex:modality ?modality . } LIMIT 20',\\n"
        "  'mentions': 'PREFIX ex: <" + EX_BASE + "> SELECT ?text ?type WHERE { ?m a ex:Mention ; ex:text ?text ; ex:entity_type ?type . } LIMIT 20',\\n"
        "  'audio_files': 'PREFIX ex: <" + EX_BASE + "> SELECT ?file ?dataset ?duration WHERE { ?a a ex:AudioRecord ; ex:file_name ?file ; ex:dataset ?dataset . OPTIONAL { ?a ex:duration_sec ?duration . } } LIMIT 20',\\n"
        "  'event_counts': 'PREFIX ex: <" + EX_BASE + "> SELECT ?event_type (COUNT(?e) AS ?count) WHERE { ?e a ex:AudioEvent ; ex:event_type ?event_type . } GROUP BY ?event_type ORDER BY DESC(?count)',\\n"
        "  'cross_modal': 'PREFIX ex: <" + EX_BASE + "> SELECT ?mention_text ?audio_event_type WHERE { ?l a ex:MultimodalAlignment ; ex:linksMention ?m ; ex:linksAudioEvent ?e . ?m ex:text ?mention_text . ?e ex:event_type ?audio_event_type . } LIMIT 20'\\n"
        "}\\n\\n"
        "for name, q in queries.items():\\n"
        "    print('\\\\n' + '='*90 + '\\\\n' + name + '\\\\n' + '='*90)\\n"
        "    for row in g.query(q):\\n"
        "        print(' | '.join(str(x) for x in row))\\n"
    )
    (PROJECT_DIR / "run_select_examples.py").write_text(text, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-download", action="store_true")
    parser.add_argument("--skip-text", action="store_true")
    parser.add_argument("--skip-circor", action="store_true")
    parser.add_argument("--skip-icbhi", action="store_true")
    parser.add_argument("--skip-images", action="store_true")
    parser.add_argument("--include-wav-download", action="store_true")
    parser.add_argument("--icbhi-source", choices=["direct", "kaggle", "local"], default="direct")
    parser.add_argument("--limit-text-docs", type=int, default=0)
    parser.add_argument("--limit-circor-records", type=int, default=0)
    parser.add_argument("--limit-icbhi-records", type=int, default=0)
    parser.add_argument("--limit-image-records", type=int, default=200)
    parser.add_argument("--image-dataset", default=IMAGE_DATASET_DEFAULT)
    parser.add_argument("--image-split", default=IMAGE_SPLIT_DEFAULT)
    parser.add_argument("--compute-audio-quality", action="store_true")
    parser.add_argument("--include-token-rdf", action="store_true")
    parser.add_argument("--export-jsonld", action="store_true")
    parser.add_argument("--copy-audio-preview", type=int, default=0)
    parser.add_argument("--max-mm-links", type=int, default=2000)
    parser.add_argument("--spacy-model", default="en_core_web_sm")
    args = parser.parse_args()

    ensure_dirs()
    tables = empty_tables()
    circor_dir = RAW_DIR / "circor-heart-sound-1.0.3" / "training_data"
    icbhi_dir = RAW_DIR / "icbhi"

    log("[1/8] download/locate datasets")
    if not args.skip_download:
        if not args.skip_circor:
            download_circor(circor_dir, include_wav=args.include_wav_download)
        if not args.skip_icbhi:
            download_icbhi(icbhi_dir, args.icbhi_source)

    log("[2/8] text annotations")
    if not args.skip_text:
        build_text_tables(tables, args.limit_text_docs, args.spacy_model)

    log("[3/8] audio annotations")
    if not args.skip_circor:
        cd = circor_dir if circor_dir.exists() else find_dir_with_files(RAW_DIR, (".wav", ".tsv"))
        if cd:
            build_circor_tables(tables, cd, args.limit_circor_records, args.compute_audio_quality)
    if not args.skip_icbhi:
        idr = find_dir_with_files(icbhi_dir, (".wav", ".txt")) or find_dir_with_files(RAW_DIR, (".wav", ".txt"))
        if idr:
            build_icbhi_tables(tables, idr, args.limit_icbhi_records, args.compute_audio_quality)

    log("[3b/8] image annotations")
    if not args.skip_images:
        build_image_tables(tables, args.image_dataset, args.image_split, args.limit_image_records)

    log("[4/8] multimodal/agent/eval layers")
    add_alignment(tables, args.max_mm_links)
    add_agent_and_eval_layers(tables)
    deduplicate_cases(tables)
    add_stats(tables)

    log("[5/8] export CSV/JSON/XML")
    export_tables(tables)

    log("[6/8] build RDF")
    g = build_rdf(tables, include_tokens=args.include_token_rdf)
    log(f"[rdf] triples={len(g)}")

    log("[7/8] run SPARQL")
    sparql_results = export_rdf_and_sparql(g, export_jsonld=args.export_jsonld)

    log("[8/8] dashboard")
    generate_dashboard(tables, sparql_results, args.copy_audio_preview)
    write_select_examples()

    log("\\nDONE")
    log(f"Project: {PROJECT_DIR}")
    log(f"Exports: {EXPORT_DIR}")
    log(f"Dashboard: {APP_DIR / 'index.html'}")
    log(f"RDF triples: {len(g)}")
    log("Table sizes:")
    for name in TABLES:
        log(f"- {name}: {len(tables[name])} rows")


if __name__ == "__main__":
    main()
