"""
This module contains classes that can be used for describe \
    data structures in the graph
"""
from rdflib import URIRef


class GraphData:
    def __init__(self, name: object, iri: object):
        self.name = name
        self.iri = iri
        self.uri_ref = URIRef(self.iri + self.name)

    def __call__(self):
        return self.uri_ref
