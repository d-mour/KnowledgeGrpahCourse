from rdflib import URIRef, BNode, Literal, Namespace, Graph, RDF, XSD
from pathlib import Path

from typing import List

# Create a Graph
g = Graph()

g.parse(f'file://{Path(__file__).parent.resolve()}/data/data.rdf', format='turtle')

# properties and classes
composedBy = URIRef('http://purl.org/ontology/mo/composer')
Soundtrack = Literal("Musical work")
genre = URIRef('https://schema.org/genre')
instrument = URIRef("http://rdaregistry.info/Elements/e/P20215")
title = URIRef('http://purl.org/dc/terms/title')
Rock = URIRef('http://service.ddex.net/dd/DD-AVS-001/dd/ddex_Rock')
Classical = URIRef('http://service.ddex.net/dd/DD-AVS-001/dd/ddex_ClassicalMusic')
Electro = URIRef('http://service.ddex.net/dd/DD-AVS-001/dd/ddex_ElectronicMusic')


def addMusic(link, name, genre: URIRef, composer, instruments: List):
    track = URIRef("https://youtu.be/" + link)
    g.add((track, RDF.type, Soundtrack))
    g.add((track, title, Literal(name)))
    g.add((track, genre, genre))
    g.add((track, composedBy, Literal(composer)))  # todo should do request by name
    for i in instruments:
        g.add((track, instrument, Literal(i)))


addMusic("GL8ZmqyNiZM", "The Prowler", Electro, 582922, ['elephant', 'drums', 'violin'])
addMusic("N1WTIstPKTY", "528491", Classical, 947, ['cello', 'piano', 'guitar'])
addMusic("B_iFRoJJLzc", "The Imperial March", Classical, 491, ['drums', 'trumpet', 'trombone'])



# Print the number of "triples" in the Graph
print(f"Graph g has {len(g)} statements.")
# Prints: Graph g has 86 statements.

# Print out the entire Graph in the RDF Turtle format
with open('data/graph.rdf', "w+", encoding="utf-8") as file:
    print(g.serialize(format="turtle"), file=file)