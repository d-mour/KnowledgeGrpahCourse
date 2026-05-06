import os
from pycocotools.coco import COCO
from pathlib import Path
import shutil
import json
import random
from ultralytics.data.converter import convert_coco

COCO_ANN = Path("coco/annotations/instances_val2017.json")
IMG_DIR = Path("coco/val2017")
OUT = Path("data_subset")
OUT_IMG = OUT / "images"
(OUT_IMG).mkdir(parents=True, exist_ok=True)

CLASSES = ["book", "clock", "bird", "cat", "dog", 'banana',
           'apple', 'pizza', 'bed', 'tv', 'bottle', 'wine glass', 'cup']
MAX_PER_CLASS = 60

coco = COCO(str(COCO_ANN))

cat_ids = coco.getCatIds(catNms=CLASSES)
print("Категории:", CLASSES, "IDs:", cat_ids)

selected_img_ids = set()
for cid in cat_ids:
    ann_ids = coco.getAnnIds(catIds=[cid])
    random.shuffle(ann_ids)
    ann_ids = ann_ids[:MAX_PER_CLASS]

    for ann in coco.loadAnns(ann_ids):
        selected_img_ids.add(ann["image_id"])

img_ids = sorted(selected_img_ids)
all_ann_ids = coco.getAnnIds(imgIds=list(selected_img_ids))
ids_with_any = set(a["image_id"] for a in coco.loadAnns(all_ann_ids))
img_ids = sorted(selected_img_ids & ids_with_any)

print(f"После фильтрации: {len(img_ids)}")

for img in coco.loadImgs(img_ids):
    src = IMG_DIR / img["file_name"]
    shutil.copy(src, OUT_IMG / img["file_name"])

anns = coco.loadAnns(coco.getAnnIds(imgIds=img_ids, catIds=cat_ids))
mini = {
    "images":      coco.loadImgs(img_ids),
    "annotations": anns,
    "categories":  coco.loadCats(cat_ids)
}
(OUT / "annotations").mkdir(exist_ok=True)
json_path = OUT / "annotations" / "instances_subset.json"
json_path.write_text(json.dumps(mini, ensure_ascii=False))

convert_coco(
    labels_dir="data_subset/annotations",
    save_dir="data_subset/yolo",
    use_segments=False,
    use_keypoints=False
)

src = "data_subset/images"
dst = "data_subset/yolo/images"
os.makedirs(dst, exist_ok=True)
for fname in os.listdir(src):
    if fname.lower().endswith((".jpg", ".jpeg", ".png")):
        shutil.copy(os.path.join(src, fname), os.path.join(dst, fname))
print("Images copied to", dst)
