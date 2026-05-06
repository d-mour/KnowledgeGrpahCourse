import json
import xml.etree.ElementTree as ET
import re
from pathlib import Path

from rdflib import Graph, Namespace, RDF, RDFS, Literal, URIRef


# paths
IMAGE_XML = "data/annotations.xml"
TEXT_JSON = "data/processed.json"
AUDIO_TEXTGRID = "data/Roblox-2026-03-28T20_04_16_970Z-converted.TextGrid"


# RDF graph init
g = Graph()
EX = Namespace("http://example.org/roblox/")
g.bind("ex", EX)


def safe_text(s):
    return s is not None and s.strip() != ""


# classes
classes = [
    EX.Session,
    EX.Frame,
    EX.ImageAnnotation,
    EX.TextAnnotation,
    EX.AudioAnnotation,
    EX.Player,
    EX.Hazard,
    EX.Disaster,
    EX.Map,
    EX.RoundResult,
]
for c in classes:
    g.add((c, RDF.type, RDFS.Class))


# properties
properties = [
    EX.hasFrame,
    EX.hasImageAnnotation,
    EX.hasTextAnnotation,
    EX.hasAudioAnnotation,
    EX.detectsObject,
    EX.mentionsPlayer,
    EX.mentionsDisaster,
    EX.mentionsMap,
    EX.hasResult,
    EX.hasLabel,
    EX.hasValue,
    EX.startTime,
    EX.endTime,
    EX.sourceFile,
    EX.hasTier,
]
for p in properties:
    g.add((p, RDF.type, RDF.Property))


# helper
def norm_id(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-zA-Z0-9а-яА-Я_]+", "_", s)
    return s.strip("_")


# root session
session = EX["session_1"]
g.add((session, RDF.type, EX.Session))


# parse image annotations XML
tree = ET.parse(IMAGE_XML)
root = tree.getroot()

for image_el in root.findall("image"):
    image_name = image_el.attrib["name"]
    frame_id = image_el.attrib["id"]

    frame_uri = EX[f"frame_{frame_id}"]
    g.add((frame_uri, RDF.type, EX.Frame))
    g.add((frame_uri, EX.sourceFile, Literal(image_name)))
    g.add((session, EX.hasFrame, frame_uri))

    ann_counter = 0

    for box in image_el.findall("box"):
        ann_counter += 1
        label = box.attrib["label"]

        ann_uri = EX[f"imgann_{frame_id}_{ann_counter}"]
        g.add((ann_uri, RDF.type, EX.ImageAnnotation))
        g.add((ann_uri, EX.hasLabel, Literal(label)))
        g.add((frame_uri, EX.hasImageAnnotation, ann_uri))

        # bbox as string
        bbox = {
            "xtl": box.attrib.get("xtl"),
            "ytl": box.attrib.get("ytl"),
            "xbr": box.attrib.get("xbr"),
            "ybr": box.attrib.get("ybr"),
        }
        g.add((ann_uri, EX.hasValue, Literal(json.dumps(bbox, ensure_ascii=False))))

        # object nodes
        if label == "player":
            obj_uri = EX[f"player_{frame_id}_{ann_counter}"]
            g.add((obj_uri, RDF.type, EX.Player))
            g.add((ann_uri, EX.detectsObject, obj_uri))

        elif label == "hazard":
            hazard_type = "unknown"
            attr = box.find("attribute")
            if attr is not None and attr.attrib.get("name") == "type":
                hazard_type = attr.text.strip()

            obj_uri = EX[f"hazard_{frame_id}_{ann_counter}_{norm_id(hazard_type)}"]
            g.add((obj_uri, RDF.type, EX.Hazard))
            g.add((obj_uri, EX.hasLabel, Literal(hazard_type)))
            g.add((ann_uri, EX.detectsObject, obj_uri))

            # if hazard corresponds to a disaster-like object
            if hazard_type in {"meteor", "tornado", "lightning", "wind"}:
                disaster_uri = EX[f"disaster_{norm_id(hazard_type)}"]
                g.add((disaster_uri, RDF.type, EX.Disaster))
                g.add((disaster_uri, EX.hasLabel, Literal(hazard_type)))
                g.add((ann_uri, EX.detectsObject, disaster_uri))

        else:
            # water / lava / ground / structure as hazards/scene objects
            obj_uri = EX[f"{label}_{frame_id}_{ann_counter}"]
            g.add((obj_uri, RDF.type, EX.Hazard))
            g.add((obj_uri, EX.hasLabel, Literal(label)))
            g.add((ann_uri, EX.detectsObject, obj_uri))

    for poly in image_el.findall("polygon"):
        ann_counter += 1
        label = poly.attrib["label"]

        ann_uri = EX[f"imgann_{frame_id}_{ann_counter}"]
        g.add((ann_uri, RDF.type, EX.ImageAnnotation))
        g.add((ann_uri, EX.hasLabel, Literal(label)))
        g.add((frame_uri, EX.hasImageAnnotation, ann_uri))
        g.add((ann_uri, EX.hasValue, Literal(poly.attrib.get("points", ""))))

        obj_uri = EX[f"{label}_{frame_id}_{ann_counter}"]
        g.add((obj_uri, RDF.type, EX.Hazard))
        g.add((obj_uri, EX.hasLabel, Literal(label)))
        g.add((ann_uri, EX.detectsObject, obj_uri))


# parse text annotations JSON
with open(TEXT_JSON, "r", encoding="utf-8") as f:
    text_data = json.load(f)

for i, item in enumerate(text_data):
    ann_uri = EX[f"textann_{i}"]
    g.add((ann_uri, RDF.type, EX.TextAnnotation))
    g.add((ann_uri, EX.sourceFile, Literal(item["file"])))
    g.add((ann_uri, EX.hasLabel, Literal(item["type"])))
    g.add((ann_uri, EX.hasValue, Literal(item["text_en"])))

    # привязываем пока к session; если хочешь — потом можно сопоставить с frame
    g.add((session, EX.hasTextAnnotation, ann_uri))

    entities = item.get("entities", {})

    if item["type"] == "PLAYER_TAG" and "player" in entities:
        player_name = entities["player"]
        player_uri = EX[f"player_name_{norm_id(player_name)}"]
        g.add((player_uri, RDF.type, EX.Player))
        g.add((player_uri, EX.hasLabel, Literal(player_name)))
        g.add((ann_uri, EX.mentionsPlayer, player_uri))

    elif item["type"] == "SURVIVORS_LIST" and "players" in entities:
        for player_name in entities["players"]:
            player_uri = EX[f"player_name_{norm_id(player_name)}"]
            g.add((player_uri, RDF.type, EX.Player))
            g.add((player_uri, EX.hasLabel, Literal(player_name)))
            g.add((ann_uri, EX.mentionsPlayer, player_uri))

    elif item["type"] == "DISASTER_WARNING" and "disaster" in entities:
        disaster_name = entities["disaster"]
        disaster_uri = EX[f"disaster_{norm_id(disaster_name)}"]
        g.add((disaster_uri, RDF.type, EX.Disaster))
        g.add((disaster_uri, EX.hasLabel, Literal(disaster_name)))
        g.add((ann_uri, EX.mentionsDisaster, disaster_uri))

    elif item["type"] == "MAP_INFO" and "map" in entities:
        map_name = entities["map"]
        map_uri = EX[f"map_{norm_id(map_name)}"]
        g.add((map_uri, RDF.type, EX.Map))
        g.add((map_uri, EX.hasLabel, Literal(map_name)))
        g.add((ann_uri, EX.mentionsMap, map_uri))

    elif item["type"] == "ROUND_RESULT" and "result" in entities:
        result_uri = EX[f"result_{norm_id(entities['result'])}"]
        g.add((result_uri, RDF.type, EX.RoundResult))
        g.add((result_uri, EX.hasLabel, Literal(entities["result"])))
        g.add((ann_uri, EX.hasResult, result_uri))


# parse TextGrid
with open(AUDIO_TEXTGRID, "r", encoding="utf-8") as f:
    tg_lines = f.readlines()

current_tier = None
interval_idx = 0
xmin_val = None
xmax_val = None
text_val = None

for line in tg_lines:
    line = line.strip()

    if line.startswith("name = "):
        m = re.search(r'name = "(.*)"', line)
        if m:
            current_tier = m.group(1)

    elif line.startswith("xmin = "):
        try:
            xmin_val = float(line.split("=")[1].strip())
        except:
            xmin_val = None

    elif line.startswith("xmax = "):
        try:
            xmax_val = float(line.split("=")[1].strip())
        except:
            xmax_val = None

    elif line.startswith("text = "):
        m = re.search(r'text = "(.*)"', line)
        if m:
            text_val = m.group(1)

            if current_tier and text_val is not None and text_val != "":
                interval_idx += 1
                ann_uri = EX[f"audioann_{current_tier}_{interval_idx}"]
                g.add((ann_uri, RDF.type, EX.AudioAnnotation))
                g.add((ann_uri, EX.hasTier, Literal(current_tier)))
                g.add((ann_uri, EX.hasLabel, Literal(text_val)))
                if xmin_val is not None:
                    g.add((ann_uri, EX.startTime, Literal(xmin_val)))
                if xmax_val is not None:
                    g.add((ann_uri, EX.endTime, Literal(xmax_val)))
                g.add((session, EX.hasAudioAnnotation, ann_uri))

                if current_tier == "disaster" and safe_text(text_val):
                    disaster_name = text_val.strip()
                    disaster_uri = EX[f"disaster_{norm_id(disaster_name)}"]
                    g.add((disaster_uri, RDF.type, EX.Disaster))
                    g.add((disaster_uri, EX.hasLabel, Literal(disaster_name)))
                    g.add((ann_uri, EX.mentionsDisaster, disaster_uri))


# save graph
out_file = "roblox_graph.ttl"
g.serialize(out_file, format="turtle")
print(f"Graph saved to {out_file}")


# sample SPARQL queries
queries = {
    "all_disasters": """
        PREFIX ex: <http://example.org/roblox/>
        SELECT DISTINCT ?d ?label
        WHERE {
            ?d a ex:Disaster .
            OPTIONAL { ?d ex:hasLabel ?label . }
        }
    """,
    "players_from_text": """
        PREFIX ex: <http://example.org/roblox/>
        SELECT DISTINCT ?player ?name
        WHERE {
            ?ann a ex:TextAnnotation ;
                 ex:mentionsPlayer ?player .
            ?player ex:hasLabel ?name .
        }
    """,
    "frames_with_meteor": """
        PREFIX ex: <http://example.org/roblox/>
        SELECT ?frame ?file
        WHERE {
            ?frame a ex:Frame ;
                   ex:sourceFile ?file ;
                   ex:hasImageAnnotation ?ann .
            ?ann ex:detectsObject ?obj .
            ?obj ex:hasLabel "meteor" .
        }
    """,
    "audio_disaster_segments": """
        PREFIX ex: <http://example.org/roblox/>
        SELECT ?ann ?start ?end ?label
        WHERE {
            ?ann a ex:AudioAnnotation ;
                 ex:hasTier "disaster" ;
                 ex:startTime ?start ;
                 ex:endTime ?end ;
                 ex:hasLabel ?label .
        }
        ORDER BY ?start
    """,
}

for name, query in queries.items():
    print(f"\\n--- {name} ---")
    for row in g.query(query):
        print(row)
