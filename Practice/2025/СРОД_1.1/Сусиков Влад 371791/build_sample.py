import json
from pathlib import Path
import shutil

BASE = Path("data_subset")
ANN_IN = BASE / "annotations" / "instances_subset.json"
IMG_IN = BASE / "images"
OUT = Path("sample_dataset")
OUT_IMG = OUT / "images"
OUT_ANN = OUT / "annotations.json"

SAMPLE_IDS = {
    "book":  ["images/000000026564.jpg", "images/000000037740.jpg"],
    "clock": ["images/000000001296.jpg", "images/000000036678.jpg"],
    "bird":  ["images/000000049761.jpg", "images/000000120420.jpg"],
    "cat":   ["images/000000084650.jpg", "images/000000134882.jpg"],
    "dog":   ["images/000000052891.jpg", "images/000000067213.jpg"]
}

full = json.loads(ANN_IN.read_text(encoding="utf8"))

wanted_files = set(Path(p).name for group in SAMPLE_IDS.values()
                   for p in group)

images_filt = [img for img in full["images"]
               if img["file_name"] in wanted_files]
anns_filt = [a for a in full["annotations"]
             if a["image_id"] in {img["id"] for img in images_filt}]

cats_filt = full["categories"]

OUT.mkdir(exist_ok=True)
OUT_IMG.mkdir(exist_ok=True)

with open(OUT_ANN, "w", encoding="utf8") as f:
    json.dump({"images": images_filt,
               "annotations": anns_filt,
               "categories": cats_filt},
              f, ensure_ascii=False, indent=2)

for img in images_filt:
    src = IMG_IN / img["file_name"]
    dst = OUT_IMG / img["file_name"]
    shutil.copy(src, dst)

print(
    f"Sample dataset generated: {len(images_filt)} images, {len(anns_filt)} annotations")
