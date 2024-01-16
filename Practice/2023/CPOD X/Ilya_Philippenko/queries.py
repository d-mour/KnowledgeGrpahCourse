from rdflib import URIRef, BNode, Literal, Namespace, Graph, RDF, XSD
from pathlib import Path

# Create a Graph
g = Graph()

g.parse(f'file://{Path(__file__).parent.resolve()}/data/data.rdf', format='turtle')

qres1 = g.query("""SELECT ?i ?s
                 WHERE {
                     ?i ns1:director_name ?s .
                     ?i ns1:music_contributor_name ?s .
                     ?i ns1:performance_actor ?s .
                 } """)

n = 1
for row in qres1:
    print(str(n)+": %s %s" % row)
    n += 1
