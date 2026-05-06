import csv
import json
import re
import time
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError


ROOT = Path(__file__).resolve().parents[1]
SPECIES_CSV = ROOT / "data" / "metadata" / "species_catalog.csv"
MANIFEST_CSV = ROOT / "data" / "metadata" / "download_manifest.csv"

TEXT_DIR = ROOT / "data" / "raw" / "text"
IMG_DIR = ROOT / "data" / "raw" / "images"
AUDIO_DIR = ROOT / "data" / "raw" / "audio"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; BirdsKGDownloader/1.0; +https://example.org)"
}

ENGLISH_NAME_HINTS = {
    "SP001": ["house sparrow"],
    "SP002": ["common starling", "european starling"],
    "SP003": ["great tit"],
    "SP004": ["hooded crow"],
    "SP005": ["common cuckoo"],
    "SP006": ["barn swallow"],
    "SP007": ["thrush nightingale"],
    "SP008": ["white wagtail"],
    "SP009": ["common chaffinch", "eurasian chaffinch"],
    "SP010": ["song thrush"],
}


def safe_name(value: str) -> str:
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", value).strip("_")


def normalize_text(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value or "")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return re.sub(r"\s+", " ", value).strip()


def http_get_json(url: str) -> Optional[dict]:
    req = Request(url, headers=HEADERS)
    delay = 1.0
    for attempt in range(1, 5):
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as exc:
            if exc.code == 429 and attempt < 4:
                print(f"[WARN] 429 on JSON request, retry in {delay:.1f}s: {url}")
                time.sleep(delay)
                delay *= 2
                continue
            print(f"[WARN] JSON HTTP error: {url} :: {exc}")
            return None
        except (URLError, TimeoutError) as exc:
            if attempt < 4:
                print(f"[WARN] JSON network error, retry in {delay:.1f}s: {url} :: {exc}")
                time.sleep(delay)
                delay *= 2
                continue
            print(f"[WARN] JSON request failed: {url} :: {exc}")
            return None
        except Exception as exc:
            print(f"[WARN] JSON request failed: {url} :: {exc}")
            return None
    return None


def http_download(url: str, out_path: Path) -> bool:
    req = Request(url, headers=HEADERS)
    delay = 1.0
    for attempt in range(1, 5):
        try:
            with urlopen(req, timeout=60) as resp:
                data = resp.read()
                out_path.write_bytes(data)
                return True
        except HTTPError as exc:
            if exc.code == 429 and attempt < 4:
                print(f"[WARN] 429 on download, retry in {delay:.1f}s: {out_path.name}")
                time.sleep(delay)
                delay *= 2
                continue
            print(f"[WARN] Download failed: {url} -> {out_path.name} :: {exc}")
            return False
        except (URLError, TimeoutError) as exc:
            if attempt < 4:
                print(f"[WARN] Download network error, retry in {delay:.1f}s: {out_path.name} :: {exc}")
                time.sleep(delay)
                delay *= 2
                continue
            print(f"[WARN] Download failed: {url} -> {out_path.name} :: {exc}")
            return False
        except OSError as exc:
            # Иногда на Windows ловится Errno 22; пробуем следующий кандидат.
            print(f"[WARN] File write failed: {out_path.name} :: {exc}")
            return False
        except Exception as exc:
            print(f"[WARN] Download failed: {url} -> {out_path.name} :: {exc}")
            return False
    return False


def ensure_dirs() -> None:
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)
    AUDIO_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_CSV.parent.mkdir(parents=True, exist_ok=True)


def read_species() -> List[Dict[str, str]]:
    with SPECIES_CSV.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_species(rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "species_id",
        "ru_name",
        "latin_name",
        "gbif_taxon_key",
        "text_status",
        "image_status",
        "audio_status",
        "notes",
    ]
    with SPECIES_CSV.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def append_manifest(rows: List[Dict[str, str]]) -> None:
    fieldnames = [
        "timestamp_utc",
        "species_id",
        "ru_name",
        "latin_name",
        "modality",
        "local_file",
        "source_url",
        "license",
        "source_name",
    ]
    exists = MANIFEST_CSV.exists()
    with MANIFEST_CSV.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerows(rows)


def wiki_summary(latin_name: str) -> Optional[Dict[str, str]]:
    title = latin_name.replace(" ", "_")
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(title)}"
    data = http_get_json(url)
    if not data or "extract" not in data:
        return None
    page_url = ""
    if isinstance(data.get("content_urls"), dict):
        page_url = (
            data["content_urls"]
            .get("desktop", {})
            .get("page", "")
        )
    return {
        "title": data.get("title", latin_name),
        "extract": data.get("extract", ""),
        "url": page_url or f"https://en.wikipedia.org/wiki/{title}",
        "license": "CC BY-SA 4.0 (Wikipedia content)",
    }


def download_text(sp: Dict[str, str], manifest_rows: List[Dict[str, str]]) -> bool:
    info = wiki_summary(sp["latin_name"])
    if not info:
        return False
    out_name = f'{sp["species_id"]}_text_01.txt'
    out_path = TEXT_DIR / out_name
    content = [
        f'ID: {sp["species_id"]}',
        f'RU: {sp["ru_name"]}',
        f'LATIN: {sp["latin_name"]}',
        f'SOURCE: {info["url"]}',
        f'LICENSE: {info["license"]}',
        "",
        info["title"],
        "",
        info["extract"],
        "",
    ]
    out_path.write_text("\n".join(content), encoding="utf-8")
    manifest_rows.append(
        {
            "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "species_id": sp["species_id"],
            "ru_name": sp["ru_name"],
            "latin_name": sp["latin_name"],
            "modality": "text",
            "local_file": str(out_path.relative_to(ROOT)).replace("\\", "/"),
            "source_url": info["url"],
            "license": info["license"],
            "source_name": "Wikipedia",
        }
    )
    return True


def commons_search_files(query: str, limit: int = 10) -> List[str]:
    params = {
        "action": "query",
        "list": "search",
        "srsearch": query,
        "srnamespace": "6",
        "srlimit": str(limit),
        "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urlencode(params)
    data = http_get_json(url)
    if not data or "query" not in data or "search" not in data["query"]:
        return []
    return [it.get("title", "") for it in data["query"]["search"] if it.get("title")]


def commons_imageinfo(titles: List[str]) -> List[Dict[str, str]]:
    if not titles:
        return []
    params = {
        "action": "query",
        "titles": "|".join(titles),
        "prop": "imageinfo",
        "iiprop": "url|extmetadata|mime",
        "format": "json",
    }
    url = "https://commons.wikimedia.org/w/api.php?" + urlencode(params)
    data = http_get_json(url)
    if not data or "query" not in data or "pages" not in data["query"]:
        return []

    result = []
    for p in data["query"]["pages"].values():
        iinfo = (p.get("imageinfo") or [])
        if not iinfo:
            continue
        url_value = iinfo[0].get("url", "")
        if not url_value:
            continue
        extmeta = iinfo[0].get("extmetadata", {})
        license_name = (
            (extmeta.get("LicenseShortName", {}) or {}).get("value", "Check source page")
        )
        description = (
            (extmeta.get("ImageDescription", {}) or {}).get("value", "")
            or (extmeta.get("ObjectName", {}) or {}).get("value", "")
        )
        result.append(
            {
                "url": url_value,
                "page_title": p.get("title", ""),
                "license": license_name,
                "mime": iinfo[0].get("mime", ""),
                "description": description,
            }
        )
    return result


def extension_from_url(url: str, default: str = ".jpg") -> str:
    m = re.search(r"\.(jpg|jpeg|png|webp|gif|mp3|wav|ogg)(?:\?|$)", url, flags=re.I)
    if not m:
        return default
    ext = m.group(1).lower()
    if ext == "jpeg":
        ext = "jpg"
    return "." + ext


def is_good_bird_photo(item: Dict[str, str]) -> bool:
    text = f'{item.get("page_title", "")} {item.get("description", "")}'.lower()
    # Жесткий отсев нерелевантных изображений для задачи распознавания вида.
    blocked = [
        " egg",
        " eggs",
        "nest",
        "chick",
        "chicks",
        "juvenile",
        "fledgling",
        "hatchling",
        "brood",
        "clutch",
        "oocyte",
        "embryo",
        "skeleton",
        "skull",
    ]
    return not any(token in text for token in blocked)


def is_relevant_to_species(sp: Dict[str, str], item: Dict[str, str]) -> bool:
    text = normalize_text(f'{item.get("page_title", "")} {item.get("description", "")}')
    latin = normalize_text(sp["latin_name"])
    latin_tokens = latin.split()
    if latin and latin in text:
        return True
    if len(latin_tokens) == 2 and all(tok in text for tok in latin_tokens):
        return True
    for hint in ENGLISH_NAME_HINTS.get(sp["species_id"], []):
        if normalize_text(hint) in text:
            return True
    return False


def download_images(sp: Dict[str, str], manifest_rows: List[Dict[str, str]], need: int = 3) -> int:
    # Минус-термы помогают сразу отсеять яйца/гнезда и прочие нерелевантные файлы.
    query = (
        f'{sp["latin_name"]} filetype:bitmap '
        "-egg -eggs -nest -chick -juvenile -fledgling -hatchling -brood -clutch"
    )
    file_titles = commons_search_files(query, limit=20)
    images = commons_imageinfo(file_titles)
    count = 0
    for item in images:
        if count >= need:
            break
        if not item.get("mime", "").startswith("image/"):
            continue
        if not is_relevant_to_species(sp, item):
            continue
        if not is_good_bird_photo(item):
            continue
        ext = extension_from_url(item["url"], default=".jpg")
        out_name = f'{sp["species_id"]}_img_{count + 1:02d}{ext}'
        out_path = IMG_DIR / out_name
        ok = http_download(item["url"], out_path)
        if not ok:
            continue
        count += 1
        source_page = "https://commons.wikimedia.org/wiki/" + item["page_title"].replace(" ", "_")
        manifest_rows.append(
            {
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "species_id": sp["species_id"],
                "ru_name": sp["ru_name"],
                "latin_name": sp["latin_name"],
                "modality": "image",
                "local_file": str(out_path.relative_to(ROOT)).replace("\\", "/"),
                "source_url": source_page,
                "license": item["license"],
                "source_name": "Wikimedia Commons",
            }
        )
        time.sleep(0.6)
    return count


def download_audio(sp: Dict[str, str], manifest_rows: List[Dict[str, str]], need: int = 3) -> int:
    # Берем реальные аудиофайлы из Wikimedia Commons (часто это записи Xeno-canto).
    file_titles = commons_search_files(f'{sp["latin_name"]} filetype:audio', limit=20)
    recs = commons_imageinfo(file_titles)
    count = 0
    for r in recs:
        if count >= need:
            break
        if not r.get("mime", "").startswith("audio/"):
            continue
        if not is_relevant_to_species(sp, r):
            continue
        file_url = r.get("url", "")
        if not file_url:
            continue
        ext = extension_from_url(file_url, default=".mp3")
        out_name = f'{sp["species_id"]}_aud_{count + 1:02d}{ext}'
        out_path = AUDIO_DIR / out_name
        ok = http_download(file_url, out_path)
        if not ok:
            continue
        count += 1
        source_url = "https://commons.wikimedia.org/wiki/" + r["page_title"].replace(" ", "_")
        manifest_rows.append(
            {
                "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "species_id": sp["species_id"],
                "ru_name": sp["ru_name"],
                "latin_name": sp["latin_name"],
                "modality": "audio",
                "local_file": str(out_path.relative_to(ROOT)).replace("\\", "/"),
                "source_url": source_url,
                "license": r.get("license", "Check source page"),
                "source_name": "Wikimedia Commons",
            }
        )
        time.sleep(0.6)
    return count


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--species-id", help="Process only one species, e.g. SP005")
    parser.add_argument(
        "--only-images",
        action="store_true",
        help="Download only images (no text/audio)",
    )
    args = parser.parse_args()

    ensure_dirs()
    rows = read_species()
    manifest_rows: List[Dict[str, str]] = []

    if args.species_id:
        rows = [r for r in rows if r.get("species_id") == args.species_id]
        if not rows:
            raise SystemExit(f"[ERROR] Unknown species id: {args.species_id}")

    print(f"[INFO] Root: {ROOT}")
    print(f"[INFO] Species file: {SPECIES_CSV}")
    print(f"[INFO] Species count: {len(rows)}")

    total_text = 0
    total_images = 0
    total_audio = 0

    failed_species: List[str] = []
    for row in rows:
        print(f'[INFO] Processing {row["species_id"]}: {row["latin_name"]}')
        text_ok = True if args.only_images else download_text(row, manifest_rows)
        img_count = download_images(row, manifest_rows, need=3)
        aud_count = 0 if args.only_images else download_audio(row, manifest_rows, need=3)
        total_text += 1 if text_ok else 0
        total_images += img_count
        total_audio += aud_count

        if not args.only_images:
            row["text_status"] = "done" if text_ok else "todo"
        row["image_status"] = "done" if img_count >= 3 else "todo"
        if not args.only_images:
            row["audio_status"] = "done" if aud_count >= 3 else "todo"

        notes = []
        if not text_ok and not args.only_images:
            notes.append("text_missing")
        if img_count < 3:
            notes.append(f"images_{img_count}/3")
        if aud_count < 3 and not args.only_images:
            notes.append(f"audio_{aud_count}/3")
        row["notes"] = "; ".join(notes)

        print(
            f"[INFO] Result {row['species_id']}: text={'ok' if text_ok else 'fail'}, "
            f"images={img_count}/3, audio={aud_count}/3"
        )
        if img_count < 3 or (not args.only_images and aud_count < 3):
            failed_species.append(row["species_id"])
        time.sleep(0.2)

    write_species(rows)
    if manifest_rows:
        append_manifest(manifest_rows)
    print(f"[INFO] Manifest rows appended: {len(manifest_rows)}")
    print(
        f"[INFO] Totals: text_ok={total_text}/{len(rows)}, "
        f"images={total_images}, audio={total_audio}"
    )

    # Не завершаем "успехом", если не удалось скачать ни одного изображения или аудио.
    if args.only_images:
        if total_images == 0 or failed_species:
            raise SystemExit(
                "[ERROR] Download incomplete for images. "
                f"Failed species: {', '.join(failed_species) if failed_species else 'none'}"
            )
        return
    if total_images == 0 or total_audio == 0 or failed_species:
        raise SystemExit(
            "[ERROR] Download incomplete. "
            f"Failed species: {', '.join(failed_species) if failed_species else 'none'}. "
            "Check rate limits and rerun later."
        )


if __name__ == "__main__":
    main()
