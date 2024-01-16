"""
This is the custom module for graph with some additional logic.
"""
from rdflib import Graph, URIRef
from rdflib.namespace import RDF

from .data_structures import GraphData


class CustomGraph(Graph):
    def __init__(self):
        super().__init__()
        self.classes: dict[GraphData] = {}
        self.object_properties: dict[GraphData] = {}
        self.data_properties: dict[GraphData] = {}

    def parse(self, iri: object, *args, **kwargs):
        """
        has the same args as graph.parse
        but has iri-arg that contains DB IRI-prefix
        ex: http://www.semanticweb.org/football/smt \
            (http://www.semanticweb.org/football - is IRI)
        """
        super().parse(*args, **kwargs)
        self.iri = iri

    def add_class(self, name: object):
        self.classes[name] = GraphData(name, self.iri)

    def add_object_property(self, name: object):
        self.object_properties[name] = GraphData(name, self.iri)

    def add_data_property(self, name: object):
        self.data_properties[name] = GraphData(name, self.iri)

    def get_list_classes(self):
        return list(self.classes.keys())

    def get_list_object_properties(self):
        return list(self.object_properties.keys())

    def get_list_data_properties(self):
        return list(self.data_properties.keys())

    def add_cls_instance(self, instance_name: object, class_name: object):
        assert class_name in self.classes.keys(), "class_name not in available classes"

        instance = URIRef(self.iri[:-1] + f"#{instance_name}")
        triplette = (instance, RDF.type, self.classes[class_name]())
        self.add(triplette)

        return instance_name

    def add_obj_prop_instance(
        self,
        instance_name: object,
        prop_inst_name: object,
        target_instance_name: object,
    ):
        assert (
            prop_inst_name in self.object_properties.keys()
        ), "prop_inst_name not in available properties"

        instance = URIRef(self.iri[:-1] + f"#{instance_name}")
        target_instance = URIRef(self.iri[:-1] + f"#{target_instance_name}")
        triplette = (
            instance,
            self.object_properties[prop_inst_name](),
            target_instance,
        )
        self.add(triplette)

        return instance_name, prop_inst_name, target_instance_name

    def add_data_prop_instance(
        self, instance_name: object, data_inst_name: object, value: object
    ):
        assert (
            data_inst_name in self.data_properties.keys()
        ), "prop_inst_name not in available properties"

        instance = URIRef(self.iri[:-1] + f"#{instance_name}")
        triplette = (instance, self.data_properties[data_inst_name](), value)
        self.add(triplette)

        return instance_name, data_inst_name, value
