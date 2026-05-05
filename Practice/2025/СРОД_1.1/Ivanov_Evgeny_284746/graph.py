from rdflib import Graph, URIRef
from rdflib.extras.external_graph_libs import rdflib_to_networkx_multidigraph
import networkx as nx
import matplotlib.pyplot as plt

def get_short_id(uri):
    text = uri
    if isinstance(uri, URIRef) and '#' in uri:
        text = uri.split('#')[-1]
    if len(text) > 24:
        text = f"{text[:10]}…{text[-10:]}"
    return URIRef(text)

g = Graph()
parsed = g.parse("mailru.rdf")

mapped = Graph()
for s, p, o in parsed:
    mapped.add((get_short_id(s), get_short_id(p), get_short_id(o)))

G = rdflib_to_networkx_multidigraph(mapped)

pos = nx.spectral_layout(G)
edge_labels = nx.get_edge_attributes(G, 'r')
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels)
nx.draw(G, with_labels=True)

#if not in interactive mode for
plt.show()
