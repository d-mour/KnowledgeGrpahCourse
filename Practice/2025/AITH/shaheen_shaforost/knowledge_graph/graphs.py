from typing import List, Tuple

import pandas as pd
from rdflib import Graph, Namespace, RDF, RDFS, OWL, Literal

from knowledge_graph.ontologies import Ontology
from knowledge_graph.utils import clean_string_for_graph


class GraphGenerator:

    def __init__(self, ontology: Ontology, namespace: str):
        self.ontology = ontology
        self.graph = Graph()
        self.ex = Namespace(namespace)
        self.graph.bind("music", self.ex)
        self.rfd_dict = {
            "DatatypeProperty": OWL.DatatypeProperty,
            "ObjectProperty": OWL.ObjectProperty,
            "type": RDF.type,
            "domain": RDFS.domain,
            "class": OWL.Class,
        }
        self._init_ontology_triplets()
        self.individuals_set = set()
        self.titles_map = {c: {} for c in self.ontology.classes}
        self.id_map = {c: {} for c in self.ontology.classes}

    def _init_ontology_triplets(self):
        for class_name in self.ontology.classes:
            self.add_triplet(class_name)
        for prop in self.ontology.properties.keys():
            self.add_triplet(prop)

    def _to_rdf_objets(self, entity):
        if entity in self.rfd_dict.keys():
            return self.rfd_dict[entity]
        return self.ex[entity]

    def _update_titles_map(self):
        for class_name, id_map in self.id_map.items():
            for individual, individual_id in id_map.items():
                self.titles_map[class_name][individual_id] = individual

    def load_graph_from_file(self, file_name: str, format="turtle"):
        self.graph.parse(file_name, format=format)

    def add_to_graph(self, triplet):
        triplet = [self._to_rdf_objets(t) for t in triplet]
        self.graph.add(tuple(triplet))

    def add_triplet(self, subject):
        if subject in self.ontology.classes:
            g_object = "Class"
            predicate = "type"
            self.add_to_graph((subject, predicate, g_object))
            self.graph.add((self._to_rdf_objets(subject), RDFS.label, Literal(subject)))

        elif subject in self.ontology.properties.keys():
            for key, value in self.ontology.properties[subject].items():
                self.add_to_graph((subject, key, value))

    def generate_id(self, class_name, individual):
        if individual not in self.id_map[class_name]:
            self.id_map[class_name][individual] = f"{class_name}_{len(self.id_map[class_name]) + 1}"
        return self.id_map[class_name][individual]

    def get_individual_title(self, class_name, individual_id: str):
        return self.titles_map[class_name][individual_id]

    def get_individual_id(self, individual: str):
        for class_name, id_map in self.id_map.items():
            if individual in id_map:
                return id_map[individual]
        return None

    def add_individual(self, individual, properties: List[Tuple], class_name):
        if class_name not in self.ontology.classes:
            print(f"Class {class_name} not found in the ontology")
            return
        individual_id = self.generate_id(class_name, individual)
        if individual_id in self.individuals_set:
            print(f"Individual {individual} with {individual_id} already exists")
        else:
            self.graph.add((self.ex[individual], RDF.type, self.ex[class_name]))
        for prop in properties:
            self.graph.add((self.ex[individual], self.ex[prop[0]], self.ex[prop[1]]))
        self.individuals_set.add(individual)

    def serialize(self, file_name: str, format="turtle"):
        self.graph.serialize(file_name, format=format)

    def load_dataset(self, csv_file: str, main_class_col: str, main_props: List[str] = None):
        df = pd.read_csv(csv_file)
        if main_props is None:
            main_props = self.ontology.properties
        props = {p_name: p["domain"].lower() for p_name, p in self.ontology.properties.items() if
                 "domain" in p and p_name in main_props}
        for _, row in df.iterrows():
            for class_name in self.ontology.classes:
                if class_name.lower() not in row:
                    continue
                individual = clean_string_for_graph(str(row[class_name.lower()]))
                if class_name.lower() in row:
                    if main_class_col == class_name.lower():
                        self.add_individual(individual, [
                            (prop_name, clean_string_for_graph(str(row[domain])),)
                            for prop_name, domain in props.items() if domain != class_name.lower()], class_name)
                    else:
                        self.add_individual(individual, [], class_name)

        self._update_titles_map()

    def save_triplets(self, file_name: str, as_ids=False):
        with open(file_name, "w", encoding="utf-8") as f:
            f.write("subject,predicate,object\n")
            for s, p, o in self.graph:
                if "#type" in str(p) or "#domain" in str(p) or "#label" in str(p):
                    continue
                s = str(s).split(":")[-1]
                o = str(o).split(":")[-1]
                p = str(p).split(":")[-1]
                if as_ids:
                    s = self.get_individual_id(s)
                    o = self.get_individual_id(o)
                f.write(f"{s},{p},{o}\n")
