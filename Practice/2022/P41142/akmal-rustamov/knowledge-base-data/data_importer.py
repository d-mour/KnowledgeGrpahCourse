import json

from rdflib import URIRef, Graph
from rdflib.namespace import RDF

ONTOLOGY_IRI = ""
graph = Graph()

grape_class = URIRef(f"{ONTOLOGY_IRI}#WineGrape")

region_class = URIRef(f"{ONTOLOGY_IRI}#Region")

winery_class = URIRef(f"{ONTOLOGY_IRI}#Winery")


def load_json_from_file(file_path):
    json_file = open(file_path, 'r')
    result = json.load(json_file)
    json_file.close()
    return result


def add_grape_individual(individual_id):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")

    graph.add((individual, RDF.type, grape_class))

    return individual


def add_region_individual(individual_id):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")

    graph.add((individual, RDF.type, region_class))

    return individual


def add_winery_individual(individual_id):
    individual = URIRef(f"{ONTOLOGY_IRI}#{individual_id}")

    graph.add((individual, RDF.type, winery_class))

    return individual


def fill_graph(ontology, data_format, data_path, result):
    graph.parse(ontology, format=data_format)

    grape_data_dict = load_json_from_file(f'{data_path}/grape-data.json')

    for grape in grape_data_dict:
        add_grape_individual(
            f"grape_{grape_data_dict[grape]['name'].replace(' ', '_').lower()}_"
        )

    region_data_dict = load_json_from_file(f'{data_path}/region-data.json')

    for region in region_data_dict:
        add_region_individual(
            f"region_{region_data_dict[region]['name'].replace(' ', '_').replace('(', '').replace(')', '').lower()}"
        )

    winery_data_dict = load_json_from_file(f'{data_path}/winery-data.json')

    for winery in winery_data_dict:
        add_winery_individual(
            f"winery_{winery_data_dict[winery]['name']}"
        )

    graph.serialize(destination=result, format=data_format)
