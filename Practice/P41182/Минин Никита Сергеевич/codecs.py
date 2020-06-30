import rdflib
from rdflib import Graph,BNode, Literal, RDF,RDFS,OWL, URIRef
from rdflib.namespace import XSD
import csv

g = Graph()
g.parse("Ontology.owl")
pref = dict(g.namespaces())['']
print("PREFIX is: ", pref)
g.bind('pref', pref)

predicates = {}
for s, p, o in g.triples((None, RDFS.range, None)):
    predicates[s] = o == XSD.string
predicates

file = open('data.csv', 'r')
reader = csv.reader(file, delimiter=';')
next(reader)
subjects = {}

for s, p, o in reader:
    new = BNode()
    g.add((new, RDF.type, pref + o))
    subjects[s] = new
    if predicates[pref+p]:
        g.add((subjects[s], pref + p, Literal(o)))
    else:
        g.add((subjects[s], pref + p, subjects[o]))

query_res1 = g.query(
    """SELECT ?codecs
       WHERE {
          ?object a pref:Codecs.
          ?object pref:Hascodec_name ?Codecs.
       }""")

queru_res2 = g.query(
    """SELECT ?codecs
       WHERE {
          ?object a pref:hasSpeed "5.3"
          ?object pref:hasMos "5"
       }""")


query_res3 = g.query(
    """SELECT ?frequency
        WHERE {
            ?algorithm a pref:Algorythm.
            ?algorithm pref:LCP ?codec.
            ?codec pref:hasSpeed "5.3".
        }""")

query_res1 
for row in query_res1:
    print("%s" % row)

query_res2 
for row in query_res2:
    print("подходящие кодеки для канала связи:" % row)

query_res3 
for row in query_res3:
    print("Рабочая частота:" % row)