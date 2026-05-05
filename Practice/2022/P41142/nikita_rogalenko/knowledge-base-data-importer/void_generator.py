import rdflib
from rdflib import Graph
from rdflib.void import generateVoID


def generate_void(ontology_path, data_format, void_path):
    f1_graph = Graph().parse(ontology_path, format=data_format)
    void = rdflib.void.generateVoID(f1_graph)
    void[0].serialize(destination=void_path, format=data_format)
