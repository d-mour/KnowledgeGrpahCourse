import json
from pathlib import Path
from rdflib import Graph, Namespace, Literal, RDF, RDFS
from rdflib.namespace import XSD

DATA_DIR = Path("sample_dataset/annotations")
STORY_FILE = Path("sample_dataset/stories/story_01/node.json")
TEXTS_FILE = Path("sample_dataset/stories/story_01/texts.json")

g = Graph()
EX = Namespace("http://example.org/ar/")
g.bind("ex", EX)

for c in ("Image", "Annotation", "Category", "StoryNode"):
    g.add((EX[c], RDF.type, RDFS.Class))
for p in ("fileName", "width", "height", "onImage", "hasCategory", "prompt", "reveal", "targets"):
    g.add((EX[p], RDF.type, RDF.Property))


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


imgs = load(DATA_DIR / "images.json")["images"]
anns = load(DATA_DIR / "annotations.json")["annotations"]
cats = load(DATA_DIR / "categories.json")["categories"]

for cat in cats:
    uri = EX[f"Category/{cat['name']}"]
    g.add((uri, RDF.type, EX.Category))
    g.add((uri, RDFS.label, Literal(cat["name"])))

for img in imgs:
    uri = EX[f"Image/{img['id']}"]
    g.add((uri, RDF.type, EX.Image))
    g.add((uri, EX.fileName, Literal(img["file_name"])))
    g.add((uri, EX.width, Literal(img["width"], datatype=XSD.integer)))
    g.add((uri, EX.height, Literal(img["height"], datatype=XSD.integer)))

id2name = {c["id"]: c["name"] for c in cats}
for ann in anns:
    uri = EX[f"Annotation/{ann['id']}"]
    g.add((uri, RDF.type, EX.Annotation))
    g.add((uri, EX.onImage, EX[f"Image/{ann['image_id']}"]))
    g.add((uri, EX.hasCategory, EX[f"Category/{id2name[ann['category_id']]}"]))

nodes = load(STORY_FILE)["nodes"]
texts = load(TEXTS_FILE)
for node in nodes:
    uri = EX[f"StoryNode/{node['node_id']}"]
    g.add((uri, RDF.type, EX.StoryNode))
    txt = texts[node["text_id"]]
    g.add((uri, EX.prompt, Literal(txt["prompt"])))
    g.add((uri, EX.reveal, Literal(txt["reveal"])))
    if "class_id" in node:
        g.add((uri, EX.targets, EX[f"Category/{node['class_id']}"]))

out = Path("ar_graph1.ttl")
g.serialize(destination=out, format="turtle")
