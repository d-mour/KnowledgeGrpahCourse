import requests
from rdflib import Graph, Literal, RDF, URIRef
# rdflib knows about some namespaces, like FOAF

from rdflib.namespace import FOAF , XSD

# create a Graph
from rdflib.plugins.sparql import prepareQuery

g = Graph()

person = URIRef('http://xmlns.com/foaf/0.1/Person')
nick =  URIRef('http://xmlns.com/foaf/0.1/nick')
name =  URIRef('http://xmlns.com/foaf/0.1/name')
mbox = URIRef('http://xmlns.com/foaf/0.1/mbox')

# Create an RDF URI node to use as the subject for multiple triples
donna = URIRef("http://example.org/donna")

# Add triples using store's add() method.
g.add((donna, RDF.type, person))
g.add((donna, nick, Literal("donna", lang="ed")))
g.add((donna, name, Literal("Donna Fales")))
g.add((donna, mbox, URIRef("mailto:donna@example.org")))

# Add another person
ed = URIRef("http://example.org/edward")

# Add triples using store's add() method.
g.add((ed, RDF.type, person))
g.add((ed, nick, Literal("ed", datatype=XSD.string)))
g.add((ed, name, Literal("Edward Scissorhands")))
g.add((ed, mbox, URIRef("mailto:e.scissorhands@example.org")))

# For each foaf:Person in the store, print out their mbox property's value.
print("--- printing mboxes ---")
for p in g.subjects(RDF.type, person):
    for mb in g.objects(p, mbox):
        print(mb)

q = prepareQuery(
        'SELECT ?s ?o WHERE { ?s foaf:mbox ?o .}',
        initNs = { "foaf": FOAF })

for row in g.query(q):
        print(row)