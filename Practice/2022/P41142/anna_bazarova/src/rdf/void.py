from rdflib.void import generateVoID
from rdflib import Graph


def make_void():
    g = Graph()
    g.parse("./src/resources/graph_resaved.owl")
    g_new, dataset = generateVoID(g)

    g_new.serialize(destination='./src/resources/VoID_graph.owl', format='turtle')
