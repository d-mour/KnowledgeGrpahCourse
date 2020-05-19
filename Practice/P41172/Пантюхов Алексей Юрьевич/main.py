from rdflib import Graph, Literal, RDF, URIRef
import requests

# create a Graph
g = Graph()
g.parse("GuitarShopModified.owl", format='turtle')

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

res = g.query(
    """PREFIX : <http://webprotege.stanford.edu/GuitarShop#>
    SELECT ?guitar
    WHERE {
        ?guitar a :AcousticGuitar;
                :hasManufacturer :Fender; 
                :hasPrice ?price .
        FILTER(?price > 20000)
    }""")

print('\n### Guitars ###')
for row in res:
    print(row[0].split('#')[1])

res = g.query(
    """PREFIX : <http://webprotege.stanford.edu/GuitarShop#>
    SELECT *
    WHERE {
        ?strings :isSuitableFor :AcousticGuitar; 
                :hasPrice ?price;
                :hasGauge "12-52".
        FILTER(?price < 2000)
    }""")

print('\n### Strings ###')
for row in res:
    print(row[0], row[1])

res = g.query(
    """PREFIX : <http://webprotege.stanford.edu/GuitarShop#>
    SELECT ?manufacturer
            (AVG(?price) AS ?var)
    WHERE {
        ?guitar a :ElectricGuitar;
                :hasPrice ?price;
                :hasManufacturer ?manufacturer.
        ?manufacturer a :Manufacturer.
    }
    GROUP BY ?manufacturer
    """)

print('\n### Prices ###')
for row in res:
    print(row[0], row[1])
