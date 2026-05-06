import pandas as pd
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF, RDFS

g = Graph()

EX = Namespace("http://example.org/")

g.add((EX['weapons'],RDF.type, RDFS.Class))

g.add((EX['pistols'],RDFS.subClassOf,EX["weapons"]))
g.add((EX['smgs'],RDFS.subClassOf,EX["weapons"]))
g.add((EX['shotguns'],RDFS.subClassOf,EX["weapons"]))

g.add((EX['p2000'],RDF.type, EX['pistols']))
g.add((EX['glock17'],RDF.type, EX['pistols']))
g.add((EX['cz75auto'],RDF.type, EX['pistols']))
g.add((EX['deagle'],RDF.type, EX['pistols']))

g.add((EX['nova'],RDF.type, EX['shotguns']))
g.add((EX['sawedoff'],RDF.type, EX['shotguns']))
g.add((EX['mag7'],RDF.type, EX['shotguns']))

g.add((EX['mac10'],RDF.type, EX['smgs']))
g.add((EX['mp9'],RDF.type, EX['smgs']))
g.add((EX['p90'],RDF.type, EX['smgs']))

data_images = pd.read_xml("./data/images/weapons_view.xml")
data_images = data_images[2:]

for element in data_images.iterrows():
    # print(element[1])
    name = str(element[1]["name"]).replace(".jpg", "")
    # print(name)
    g.add((EX[f"{name}"], EX['hasImage'], URIRef(f"./data/images/weapons_view/{element[1]['name']}")))
    

data_sound = pd.read_csv("./data/audio/sound_data.csv")

for element in data_sound.iterrows():
    print(element[1])
    g.add((EX[f"{element[1]['weapon']}"], EX['hasSounds'], Literal(f"{element[1]}")))
    g.add((EX[f"{element[1]['weapon']}"], EX['soundFile'], URIRef(f"./data/audio/sound.mp3")))


data_text = pd.read_csv("./data/text/token_text_2.csv")

for element in data_text.iterrows():
    print(element[1])
    g.add((EX[f"{element[1]['weapon']}"], EX['hasTokens'], Literal(f"{element[1]['token']}")))

g.serialize(destination='weapons_graph.rdf', format="xml")