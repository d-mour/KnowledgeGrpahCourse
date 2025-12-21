import json
from rdflib import Graph, URIRef, Literal, Namespace
from rdflib.namespace import RDF, RDFS

def load_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

json_data = "out.json"
data = load_json(json_data)

g = Graph()

EX = Namespace("http://example.org/skin#")
g.bind("ex", EX)

for skin in data["skins"]:
    weapon_uri = URIRef(EX[skin["Название оружия"].replace(" ", "_")])
    skin_uri = URIRef(EX[skin["Название скина"].replace(" ", "_")])

    g.add((weapon_uri, RDF.type, EX.Weapon))
    g.add((skin_uri, RDF.type, EX.Skin))
    g.add((weapon_uri, EX.hasSkin, skin_uri))

    g.add((skin_uri, EX.weaponName, Literal(skin["Название оружия"])))
    g.add((skin_uri, EX.skinName, Literal(skin["Название скина"])))
    g.add((skin_uri, EX.skinEnglishName, Literal(skin["name"])))
    g.add((skin_uri, EX.floatRange, Literal(skin["Ограничение по float range"])))
    g.add((skin_uri, EX.rarity, Literal(skin["Редкость"])))
    g.add((skin_uri, EX.collection, Literal(skin["Коллекция"])))
    g.add((skin_uri, EX.operation, Literal(skin["Операция"])))
    g.add((skin_uri, EX.description, Literal(skin["Описание рисунка на скине"])))
    g.add((skin_uri, EX.colors, Literal(skin["Преобладающие цвета которые используются"])))
    g.add((skin_uri, EX.quality, Literal(skin["Качество"])))

    info = skin["Информация"]
    g.add((skin_uri, EX.maxPrice, Literal(info["max"])))
    g.add((skin_uri, EX.minPrice, Literal(info["min"])))
    g.add((skin_uri, EX.averagePrice, Literal(info["average"])))

    for timestamp, price in info["history"]:
        history_uri = URIRef(EX[f"history_{timestamp}"])
        g.add((history_uri, RDF.type, EX.History))
        g.add((history_uri, EX.timestamp, Literal(timestamp)))
        g.add((history_uri, EX.price, Literal(price)))
        g.add((skin_uri, EX.hasHistory, history_uri))

    for offer in skin.get("Предложения", []):
        offer_uri = URIRef(EX[f"offer_{offer['price']}"])
        g.add((offer_uri, RDF.type, EX.Offer))
        g.add((offer_uri, EX.price, Literal(offer["price"])))
        g.add((offer_uri, EX.total, Literal(offer["total"])))
        g.add((skin_uri, EX.hasOffer, offer_uri))

output_file = "skins.rdf"
with open(output_file, "w", encoding="utf-8") as f:
    f.write(g.serialize(format="xml"))

print(f"RDF данные сохранены в {output_file}")
