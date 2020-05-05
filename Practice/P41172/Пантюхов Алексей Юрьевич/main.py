from rdflib import Graph, Literal, RDF, URIRef
import requests

# create a Graph
g = Graph()
g.parse("GuitarShop.owl", format='turtle')

# loop through each triple in the graph (subj, pred, obj)
for subj, pred, obj in g:
    # check if there is at least one triple in the Graph
    if (subj, pred, obj) not in g:
        raise Exception("It better be!")
    if g.label(subj):
        print(g.label(subj))

# print the number of "triples" in the Graph
print("graph has {} statements.".format(len(g)))
# prints graph has 86 statements.

# print out the entire Graph in the RDF Turtle format
# print(g.serialize(format="turtle").decode("utf-8"))

res = g.query(
    """PREFIX : <http://webprotege.stanford.edu/GuitarShop#>
    SELECT ?guitar
    WHERE {
        ?guitar :hasManufacturer :Fender; 
                :hasPrice ?price .
        FILTER(?price > 500)
    }""")

for row in res:
    print(row[0])
