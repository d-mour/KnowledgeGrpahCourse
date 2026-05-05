from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from rdflib import Graph, Literal, Namespace, RDF, XSD


ROOT = Path(__file__).resolve().parents[1]
SPECIES_CSV = ROOT / "data" / "metadata" / "species_catalog.csv"
TEXT_DIR = ROOT / "data" / "annotations" / "text"
AUDIO_DIR = ROOT / "data" / "annotations" / "audio"
IMAGE_JSON = ROOT / "data" / "annotations" / "images" / "instances_default.json"

ONTOLOGY_TTL = ROOT / "ontology" / "birds_ontology.ttl"
INSTANCES_TTL = ROOT / "ontology" / "birds_instances.ttl"
KG_TTL = ROOT / "ontology" / "birds_kg.ttl"


EX = Namespace("http://example.org/birds#")


@dataclass
class Mention:
    mention_id: str
    label: str
    text: str
    start: int
    end: int
    species_id: Optional[str]


@dataclass
class AudioSeg:
    seg_id: str
    start: float
    end: float
    species_id: Optional[str]
    signal_type: Optional[str]
    overlap_flag: Optional[str]
    is_background: bool
    background_type: Optional[str]
    background_intensity: Optional[str]


def sanitize_label(v: str) -> str:
    if not v:
        return ""
    s = v.replace("\\_", "_")
    s = re.sub(r"\[\d+\]", "", s)
    s = s.replace("*", "").strip()
    if s == "_":
        return ""
    return s


def parse_tsv_mentions(path: Path) -> List[Mention]:
    mentions: Dict[str, Mention] = {}
    seq = 0

    for raw in path.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        parts = raw.split("\t")
        if len(parts) < 6:
            continue

        token = parts[2]
        off = parts[1]
        canonical = parts[3]
        label_raw = parts[4]
        species_raw = parts[5]

        m_off = re.match(r"(\d+)-(\d+)", off)
        if not m_off:
            continue
        start, end = int(m_off.group(1)), int(m_off.group(2))

        label = sanitize_label(label_raw)
        if not label:
            continue

        sid_match = re.search(r"\[(\d+)\]", label_raw or canonical or species_raw)
        if sid_match:
            key = sid_match.group(1)
        else:
            seq += 1
            key = f"line{seq}"

        species_val = sanitize_label(species_raw)
        if species_val in {"", "_"}:
            species_val = None

        mention = mentions.get(key)
        if mention is None:
            mentions[key] = Mention(
                mention_id=key,
                label=label,
                text=token,
                start=start,
                end=end,
                species_id=species_val,
            )
        else:
            mention.start = min(mention.start, start)
            mention.end = max(mention.end, end)
            mention.text = f"{mention.text} {token}"
            if not mention.species_id and species_val:
                mention.species_id = species_val

    return list(mentions.values())


def parse_kv(text: str) -> Dict[str, str]:
    out: Dict[str, str] = {}
    for part in (text or "").split(";"):
        if "=" not in part:
            continue
        k, v = part.split("=", 1)
        out[k.strip()] = v.strip()
    return out


def parse_textgrid_segments(path: Path) -> List[AudioSeg]:
    lines = path.read_text(encoding="utf-8").splitlines()
    segs: List[AudioSeg] = []
    tier = None
    xmin = None
    xmax = None
    text = None
    idx = 0

    for line in lines:
        s = line.strip()
        if s.startswith('name = "'):
            if "BirdCallSegment" in s:
                tier = "BirdCallSegment"
            elif "BackgroundSound" in s:
                tier = "BackgroundSound"
            else:
                tier = None
            continue

        if s.startswith("xmin = "):
            try:
                xmin = float(s.replace("xmin = ", "").strip())
            except ValueError:
                xmin = None
            continue
        if s.startswith("xmax = "):
            try:
                xmax = float(s.replace("xmax = ", "").strip())
            except ValueError:
                xmax = None
            continue
        if s.startswith('text = "'):
            text = s[len('text = "'):-1] if s.endswith('"') else ""
            if tier in {"BirdCallSegment", "BackgroundSound"} and xmin is not None and xmax is not None:
                idx += 1
                kv = parse_kv(text or "")
                if tier == "BirdCallSegment":
                    segs.append(
                        AudioSeg(
                            seg_id=f"{path.stem}_seg_{idx}",
                            start=xmin,
                            end=xmax,
                            species_id=kv.get("species_id"),
                            signal_type=kv.get("signal_type"),
                            overlap_flag=kv.get("overlap_flag"),
                            is_background=False,
                            background_type=None,
                            background_intensity=None,
                        )
                    )
                else:
                    segs.append(
                        AudioSeg(
                            seg_id=f"{path.stem}_bg_{idx}",
                            start=xmin,
                            end=xmax,
                            species_id=None,
                            signal_type=None,
                            overlap_flag=None,
                            is_background=True,
                            background_type=kv.get("type"),
                            background_intensity=kv.get("intensity"),
                        )
                    )
            xmin = None
            xmax = None
            text = None
    return segs


def build_graph() -> Graph:
    g = Graph()
    g.bind("ex", EX)

    # Species
    species_nodes: Dict[str, str] = {}
    with SPECIES_CSV.open("r", encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            sid = row["species_id"]
            s_uri = EX[f"species/{sid}"]
            species_nodes[sid] = s_uri
            g.add((s_uri, RDF.type, EX.BirdSpecies))
            g.add((s_uri, EX.speciesId, Literal(sid)))
            g.add((s_uri, EX.russianName, Literal(row["ru_name"])))
            g.add((s_uri, EX.latinName, Literal(row["latin_name"])))
            g.add((s_uri, EX.gbifTaxonKey, Literal(row["gbif_taxon_key"])))

    # Text annotations
    for tsv in sorted(TEXT_DIR.glob("*.tsv")):
        doc_uri = EX[f"text/{tsv.stem}"]
        g.add((doc_uri, RDF.type, EX.TextDocument))
        g.add((doc_uri, EX.fileName, Literal(tsv.name)))
        mentions = parse_tsv_mentions(tsv)
        for m in mentions:
            m_uri = EX[f"textMention/{tsv.stem}_{m.mention_id}"]
            g.add((m_uri, RDF.type, EX.TextMention))
            g.add((m_uri, EX.mentionLabel, Literal(m.label)))
            g.add((m_uri, EX.mentionText, Literal(m.text)))
            g.add((m_uri, EX.startOffset, Literal(m.start, datatype=XSD.integer)))
            g.add((m_uri, EX.endOffset, Literal(m.end, datatype=XSD.integer)))
            g.add((doc_uri, EX.hasTextMention, m_uri))
            if m.species_id and m.species_id in species_nodes:
                g.add((m_uri, EX.aboutSpecies, EX[f"species/{m.species_id}"]))

    # Audio annotations
    for tg in sorted(AUDIO_DIR.glob("*.TextGrid")):
        rec_uri = EX[f"audio/{tg.stem}"]
        g.add((rec_uri, RDF.type, EX.AudioRecording))
        g.add((rec_uri, EX.fileName, Literal(tg.name)))
        for seg in parse_textgrid_segments(tg):
            if seg.is_background:
                s_uri = EX[f"backgroundSegment/{seg.seg_id}"]
                g.add((s_uri, RDF.type, EX.BackgroundSegment))
                g.add((rec_uri, EX.hasBackgroundSegment, s_uri))
                g.add((s_uri, EX.startTime, Literal(seg.start, datatype=XSD.double)))
                g.add((s_uri, EX.endTime, Literal(seg.end, datatype=XSD.double)))
                if seg.background_type:
                    g.add((s_uri, EX.backgroundType, Literal(seg.background_type)))
                if seg.background_intensity:
                    g.add((s_uri, EX.backgroundIntensity, Literal(seg.background_intensity)))
            else:
                s_uri = EX[f"audioSegment/{seg.seg_id}"]
                g.add((s_uri, RDF.type, EX.AudioSegment))
                g.add((rec_uri, EX.hasAudioSegment, s_uri))
                g.add((s_uri, EX.startTime, Literal(seg.start, datatype=XSD.double)))
                g.add((s_uri, EX.endTime, Literal(seg.end, datatype=XSD.double)))
                if seg.signal_type:
                    g.add((s_uri, EX.signalType, Literal(seg.signal_type)))
                if seg.overlap_flag:
                    g.add((s_uri, EX.overlapFlag, Literal(seg.overlap_flag)))
                if seg.species_id and seg.species_id in species_nodes:
                    g.add((s_uri, EX.segmentSpecies, EX[f"species/{seg.species_id}"]))

    # Image annotations (COCO)
    with IMAGE_JSON.open("r", encoding="utf-8") as f:
        coco = json.load(f)
    img_by_id = {img["id"]: img for img in coco.get("images", [])}
    for img in coco.get("images", []):
        i_uri = EX[f"image/{img['id']}"]
        g.add((i_uri, RDF.type, EX.Image))
        g.add((i_uri, EX.fileName, Literal(img["file_name"])))

    for ann in coco.get("annotations", []):
        image_id = ann["image_id"]
        d_uri = EX[f"detection/{ann['id']}"]
        i_uri = EX[f"image/{image_id}"]
        g.add((d_uri, RDF.type, EX.BirdDetection))
        g.add((i_uri, EX.hasDetection, d_uri))
        bbox = ann.get("bbox", [0, 0, 0, 0])
        g.add((d_uri, EX.bboxX, Literal(float(bbox[0]), datatype=XSD.double)))
        g.add((d_uri, EX.bboxY, Literal(float(bbox[1]), datatype=XSD.double)))
        g.add((d_uri, EX.bboxWidth, Literal(float(bbox[2]), datatype=XSD.double)))
        g.add((d_uri, EX.bboxHeight, Literal(float(bbox[3]), datatype=XSD.double)))
        attrs = ann.get("attributes", {}) or {}
        if "occluded" in attrs:
            g.add((d_uri, EX.occluded, Literal(bool(attrs["occluded"]), datatype=XSD.boolean)))
        sid = attrs.get("species_id")
        if sid and sid in species_nodes:
            g.add((d_uri, EX.detectedSpecies, EX[f"species/{sid}"]))

    return g


def main() -> None:
    g = build_graph()
    INSTANCES_TTL.parent.mkdir(parents=True, exist_ok=True)
    g.serialize(INSTANCES_TTL, format="turtle")

    g_full = Graph()
    g_full.parse(ONTOLOGY_TTL, format="turtle")
    g_full.parse(INSTANCES_TTL, format="turtle")
    g_full.serialize(KG_TTL, format="turtle")
    print(f"Instances: {INSTANCES_TTL}")
    print(f"Knowledge graph: {KG_TTL}")
    print(f"Triples: {len(g_full)}")


if __name__ == "__main__":
    main()
