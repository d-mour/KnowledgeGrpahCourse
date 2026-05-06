import json
import os
import re
from datetime import datetime

from urllib.parse import quote
from rdflib import Graph, Namespace, RDF, RDFS, URIRef, Literal
from rdflib.namespace import OWL, XSD


def create_graph():
    # --------------------- Пространство имен

    NS = Namespace("http://www.semanticweb.org/danis/ontologies/2024/12/dead-by-daylight/v1/")

    # --------------------- Создаем граф

    g = Graph()
    g.bind("ns", NS)

    # --------------------- Class

    # Perk
    g.add((NS.Perk, RDF.type, RDFS.Class))
    # Build
    g.add((NS.Build, RDF.type, RDFS.Class))
    # Killer
    g.add((NS.Killer, RDF.type, RDFS.Class))
    # Survivor
    g.add((NS.Survivor, RDF.type, RDFS.Class))
    # Snapshot
    g.add((NS.Snapshot, RDF.type, RDFS.Class))

    # --------------------- Object Property

    # hasPerk
    g.add((NS.hasPerk, RDF.type, OWL.ObjectProperty))  # тип элемента графа
    g.add((NS.hasPerk, RDFS.domain, NS.Build))  # domain
    g.add((NS.hasPerk, RDFS.range, NS.Perk))  # range

    g.add((NS.hasSnapshot, RDF.type, OWL.ObjectProperty))  # тип элемента графа
    g.add((NS.hasSnapshot, RDFS.domain, NS.Perk))  # domain
    g.add((NS.hasSnapshot, RDFS.domain, NS.Build))  # domain
    g.add((NS.hasSnapshot, RDFS.range, NS.Snapshot))  # range

    g.add((NS.isInClass, RDF.type, OWL.ObjectProperty))  # тип элемента графа
    g.add((NS.isInClass, RDFS.domain, NS.Perk))  # domain
    g.add((NS.isInClass, RDFS.domain, NS.Build))  # domain
    g.add((NS.isInClass, RDFS.range, NS.Killer))  # range
    g.add((NS.isInClass, RDFS.range, NS.Survivor))  # range

    # --------------------- Data property

    # date
    g.add((NS.date, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.date, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.date, RDFS.range, XSD.date))  # range

    # escapeRate
    g.add((NS.escapeRate, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.escapeRate, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.escapeRate, RDFS.range, XSD.float))  # range

    # pickRate
    g.add((NS.pickRate, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.pickRate, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.pickRate, RDFS.range, XSD.float))  # range

    # matchCount
    g.add((NS.matchCount, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.matchCount, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.matchCount, RDFS.range, XSD.int))  # range

    # survivorCount
    g.add((NS.survivorCount, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.survivorCount, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.survivorCount, RDFS.range, XSD.int))  # range

    # escapeCount
    g.add((NS.escapeCount, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.escapeCount, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.escapeCount, RDFS.range, XSD.int))  # range

    # killRate
    g.add((NS.killRate, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.killRate, RDFS.domain, NS.Snapshot))  # domain
    g.add((NS.killRate, RDFS.range, XSD.float))  # range

    return g, NS

# TODO: костыль №1
def create_graph_for_embeddings():
    # --------------------- Пространство имен

    NS = Namespace("http://www.semanticweb.org/danis/ontologies/2024/12/dead-by-daylight/v2/")

    # --------------------- Создаем граф

    g = Graph()
    g.bind("ns", NS)

    # --------------------- Class

    # Perk
    g.add((NS.Perk, RDF.type, RDFS.Class))
    # Build
    g.add((NS.Build, RDF.type, RDFS.Class))
    # Killer
    g.add((NS.Killer, RDF.type, RDFS.Class))
    # Survivor
    g.add((NS.Survivor, RDF.type, RDFS.Class))

    # --------------------- Object Property

    # hasPerk
    g.add((NS.hasPerk, RDF.type, OWL.ObjectProperty))  # тип элемента графа
    g.add((NS.hasPerk, RDFS.domain, NS.Build))  # domain
    g.add((NS.hasPerk, RDFS.range, NS.Perk))  # range

    g.add((NS.isInClass, RDF.type, OWL.ObjectProperty))  # тип элемента графа
    g.add((NS.isInClass, RDFS.domain, NS.Perk))  # domain
    g.add((NS.isInClass, RDFS.domain, NS.Build))  # domain
    # ------------------- добавленное
    g.add((NS.isInClass, RDFS.domain, NS.Killer))  # range
    g.add((NS.isInClass, RDFS.domain, NS.Survivor))  # range
    # -------------------------------
    g.add((NS.isInClass, RDFS.range, NS.Killer))  # range
    g.add((NS.isInClass, RDFS.range, NS.Survivor))  # range

    # --------------------- Data property

    # escapeRate
    g.add((NS.escapeRate, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.escapeRate, RDFS.domain, NS.Perk))  # domain
    g.add((NS.escapeRate, RDFS.domain, NS.Build))  # domain
    g.add((NS.escapeRate, RDFS.domain, NS.Survivor))  # domain
    g.add((NS.escapeRate, RDFS.range, XSD.float))  # range

    # pickRate
    g.add((NS.pickRate, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.pickRate, RDFS.domain, NS.Perk))  # domain
    g.add((NS.pickRate, RDFS.domain, NS.Build))  # domain
    g.add((NS.pickRate, RDFS.domain, NS.Survivor))  # domain
    g.add((NS.pickRate, RDFS.domain, NS.Killer))  # domain
    g.add((NS.pickRate, RDFS.range, XSD.float))  # range

    # matchCount
    g.add((NS.matchCount, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.matchCount, RDFS.domain, NS.Perk))  # domain
    g.add((NS.matchCount, RDFS.domain, NS.Survivor))  # domain
    g.add((NS.matchCount, RDFS.domain, NS.Killer))  # domain
    g.add((NS.matchCount, RDFS.range, XSD.int))  # range

    # survivorCount
    g.add((NS.survivorCount, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.survivorCount, RDFS.domain, NS.Perk))  # domain
    g.add((NS.survivorCount, RDFS.domain, NS.Build))  # domain
    g.add((NS.survivorCount, RDFS.range, XSD.int))  # range

    # escapeCount
    g.add((NS.escapeCount, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.escapeCount, RDFS.domain, NS.Perk))  # domain
    g.add((NS.escapeCount, RDFS.domain, NS.Build))  # domain
    g.add((NS.escapeCount, RDFS.range, XSD.int))  # range

    # killRate
    g.add((NS.killRate, RDF.type, OWL.DatatypeProperty))  # тип элемента графа
    g.add((NS.killRate, RDFS.domain, NS.Killer))  # domain
    g.add((NS.killRate, RDFS.range, XSD.float))  # range

    return g, NS


# --------------------- метод создания URI для онтологии

def valid_readable_uri(name: str):
    name = re.sub(r"[&'\s:-]+", '_', name)
    return quote(name, safe='')


def create_ontology():

    g, NS = create_graph()
    g2, NS2 = create_graph_for_embeddings()

    # --------------------- Создание объектов со связями и свойствами

    # --------------------- Perks

    def add_perks_g(g: Graph, NS: Namespace, role: str):
        directory_path = lambda role: f"../data/{role}/perk/result"

        file_names = [f for f in os.listdir(directory_path(role)) if
                      os.path.isfile(os.path.join(directory_path(role), f))]
        for file_name in file_names:
            with open(f"{directory_path(role)}/{file_name}", "r", encoding="utf-8") as data_file:
                data = json.load(data_file)["data"]

                for perk in data:
                    new_perk = URIRef(NS[valid_readable_uri(perk.get("name"))])
                    g.add((new_perk, RDF.type, NS.Perk))
                    new_snapshot = URIRef(
                        NS[quote(f"{role}_perk/{file_name.split('.')[0]}/{perk.get('name')}", safe='')])
                    g.add((new_snapshot, RDF.type, NS.Snapshot))

                    g.add((new_perk, NS.hasSnapshot, new_snapshot))

                    if role == "killer":
                        g.add((new_perk, NS.isInClass, NS.Killer))  # range
                    elif role == "survivor":
                        g.add((new_perk, NS.isInClass, NS.Survivor))

                    snapshot_date = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d").date()
                    g.add((new_snapshot, NS.date, Literal(snapshot_date, datatype=XSD.date)))

                    g.add((new_snapshot, NS.escapeRate, Literal(float(perk.get("escape_rate")), datatype=XSD.float)))
                    g.add((new_snapshot, NS.pickRate, Literal(float(perk.get("pick_rate")), datatype=XSD.float)))
                    g.add((new_snapshot, NS.survivorCount, Literal(int(perk.get("survivors")), datatype=XSD.int)))
                    g.add((new_snapshot, NS.matchCount, Literal(int(perk.get("count")), datatype=XSD.int)))
                    g.add((new_snapshot, NS.escapeCount, Literal(int(perk.get("escapes")), datatype=XSD.int)))

    add_perks_g(g, NS, "killer")
    add_perks_g(g, NS, "survivor")

    # TODO: костыль №2 (все методы с концом на eg)
    def add_perks_eg(g: Graph, NS: Namespace, role: str):
        directory_path = lambda role: f"../data/{role}/perk/result"

        file_name = [f for f in os.listdir(directory_path(role)) if
                      os.path.isfile(os.path.join(directory_path(role), f))][0]

        with open(f"{directory_path(role)}/{file_name}", "r", encoding="utf-8") as data_file:
            data = json.load(data_file)["data"]

            for perk in data:
                new_perk = URIRef(NS[valid_readable_uri(perk.get("name"))])
                g.add((new_perk, RDF.type, NS.Perk))

                if role == "killer":
                    g.add((new_perk, NS.isInClass, NS.Killer))  # range
                elif role == "survivor":
                    g.add((new_perk, NS.isInClass, NS.Survivor))

                g.add((new_perk, NS.escapeRate, Literal(float(perk.get("escape_rate")), datatype=XSD.float)))
                g.add((new_perk, NS.pickRate, Literal(float(perk.get("pick_rate")), datatype=XSD.float)))
                g.add((new_perk, NS.survivorCount, Literal(int(perk.get("survivors")), datatype=XSD.int)))
                g.add((new_perk, NS.matchCount, Literal(int(perk.get("count")), datatype=XSD.int)))
                g.add((new_perk, NS.escapeCount, Literal(int(perk.get("escapes")), datatype=XSD.int)))


    add_perks_eg(g2, NS2,"killer")
    add_perks_eg(g2, NS2,"survivor")

    # --------------------- Characters

    def add_characters_g(g: Graph, NS: Namespace, role: str):
        directory_path = lambda role: f"../data/{role}/character/result"
        file_names = [f for f in os.listdir(directory_path(role)) if
                      os.path.isfile(os.path.join(directory_path(role), f))]
        for file_name in file_names:
            with open(f"{directory_path(role)}/{file_name}", "r", encoding="utf-8") as data_file:
                data = json.load(data_file)["data"]

                if role == "killer":
                    for character in data:
                        new_character = URIRef(NS[valid_readable_uri(character.get("name"))])
                        g.add((new_character, RDF.type, NS.Killer))
                        new_snapshot = URIRef(
                            NS[quote(f"{role}/{file_name.split('.')[0]}/{character.get('name')}", safe='')])
                        g.add((new_snapshot, RDF.type, NS.Snapshot))

                        g.add((new_character, NS.hasSnapshot, new_snapshot))

                        snapshot_date = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d").date()
                        g.add((new_snapshot, NS.date, Literal(snapshot_date, datatype=XSD.date)))

                        g.add((new_snapshot, NS.killRate, Literal(float(character.get("kill_rate")), datatype=XSD.float)))
                        g.add((new_snapshot, NS.pickRate, Literal(float(character.get("pick_rate")), datatype=XSD.float)))
                        g.add((new_snapshot, NS.matchCount, Literal(int(character.get("matches")), datatype=XSD.int)))
                elif role == "survivor":
                    for character in data:
                        new_character = URIRef(NS[valid_readable_uri(character.get("name"))])
                        g.add((new_character, RDF.type, NS.Survivor))
                        new_snapshot = URIRef(
                            NS[quote(f"{role}/{file_name.split('.')[0]}/{character.get('name')}", safe='')])
                        g.add((new_snapshot, RDF.type, NS.Snapshot))

                        g.add((new_character, NS.hasSnapshot, new_snapshot))

                        snapshot_date = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d").date()
                        g.add((new_snapshot, NS.date, Literal(snapshot_date, datatype=XSD.date)))

                        g.add((new_snapshot, NS.escapeRate,
                               Literal(float(character.get("escape_rate")), datatype=XSD.float)))
                        g.add(
                            (new_snapshot, NS.pickRate, Literal(float(character.get("pick_rate")), datatype=XSD.float)))
                        g.add((new_snapshot, NS.matchCount, Literal(int(character.get("count")), datatype=XSD.int)))

    add_characters_g(g, NS, "killer")
    add_characters_g(g, NS, "survivor")

    def add_characters_eg(g: Graph, NS: Namespace, role: str):
        directory_path = lambda role: f"../data/{role}/character/result"
        file_name = [f for f in os.listdir(directory_path(role)) if
                      os.path.isfile(os.path.join(directory_path(role), f))][0]
        with open(f"{directory_path(role)}/{file_name}", "r", encoding="utf-8") as data_file:
            data = json.load(data_file)["data"]

            if role == "killer":
                for character in data:
                    new_character = URIRef(NS[valid_readable_uri(character.get("name"))])
                    g.add((new_character, RDF.type, NS.Killer))

                    g.add((new_character, NS.killRate, Literal(float(character.get("kill_rate")), datatype=XSD.float)))
                    g.add((new_character, NS.pickRate, Literal(float(character.get("pick_rate")), datatype=XSD.float)))
                    g.add((new_character, NS.matchCount, Literal(int(character.get("matches")), datatype=XSD.int)))
                    # ------------------- добавленное
                    g.add((new_character, NS.isInClass, NS.Killer))
            elif role == "survivor":
                for character in data:
                    new_character = URIRef(NS[valid_readable_uri(character.get("name"))])
                    g.add((new_character, RDF.type, NS.Survivor))

                    g.add((new_character, NS.escapeRate, Literal(float(character.get("escape_rate")), datatype=XSD.float)))
                    g.add((new_character, NS.pickRate, Literal(float(character.get("pick_rate")), datatype=XSD.float)))
                    g.add((new_character, NS.matchCount, Literal(int(character.get("count")), datatype=XSD.int)))
                    # ------------------- добавленное
                    g.add((new_character, NS.isInClass, NS.Survivor))


    add_characters_eg(g2, NS2, "killer")
    add_characters_eg(g2, NS2, "survivor")

    # --------------------- Builds

    def add_builds_g(g: Graph, NS: Namespace, role: str):
        directory_path = lambda role: f"../data/{role}/build/result"

        file_names = [f for f in os.listdir(directory_path(role)) if
                      os.path.isfile(os.path.join(directory_path(role), f))]
        for file_name in file_names:
            with open(f"{directory_path(role)}/{file_name}", "r", encoding="utf-8") as data_file:
                data = json.load(data_file)

                for i, build in enumerate(data, start=1):
                    new_build = URIRef(NS[f"{role[0].upper() + role[1:]}_Build_{i}"])
                    g.add((new_build, RDF.type, NS.Build))
                    new_snapshot = URIRef(
                        NS[quote(f"{role}_build/{file_name.split('.')[0]}/{role[0].upper() + role[1:]}_Build_{i}", safe='')])
                    g.add((new_snapshot, RDF.type, NS.Snapshot))

                    g.add((new_build, NS.hasSnapshot, new_snapshot))

                    snapshot_date = datetime.strptime(file_name.split(".")[0], "%Y-%m-%d").date()
                    g.add((new_snapshot, NS.date, Literal(snapshot_date, datatype=XSD.date)))

                    for perk in build.get("build"):
                        perk = NS[valid_readable_uri(perk)]
                        g.add((new_build, NS.hasPerk, perk))

                    # TODO: костыль №3
                    if len(build.get("build")) == 3:
                        perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk4))
                    elif len(build.get("build")) == 2:
                        perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk4))
                        perk3 = NS[valid_readable_uri("Third Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk3))
                    elif len(build.get("build")) == 1:
                        perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk4))
                        perk3 = NS[valid_readable_uri("Third Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk3))
                        perk2 = NS[valid_readable_uri("Second Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk2))
                    elif len(build.get("build")) == 0:
                        perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk4))
                        perk3 = NS[valid_readable_uri("Third Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk3))
                        perk2 = NS[valid_readable_uri("Second Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk2))
                        perk1 = NS[valid_readable_uri("First Empty Slot")]
                        g.add((new_build, NS.hasPerk, perk1))

                    g.add((new_snapshot, NS.escapeRate, Literal(float(build.get("escapeRate")), datatype=XSD.float)))
                    g.add((new_snapshot, NS.pickRate, Literal(float(build.get("usage")), datatype=XSD.float)))
                    g.add((new_snapshot, NS.escapeCount, Literal(int(build.get("escapes")), datatype=XSD.int)))
                    g.add((new_snapshot, NS.survivorCount, Literal(int(build.get("survivors")), datatype=XSD.int)))

    add_builds_g(g, NS, "killer")
    add_builds_g(g, NS, "survivor")

    def add_builds_eg(g: Graph, NS: Namespace, role: str):
        directory_path = lambda role: f"../data/{role}/build/result"

        file_name = [f for f in os.listdir(directory_path(role)) if
                      os.path.isfile(os.path.join(directory_path(role), f))][0]
        with open(f"{directory_path(role)}/{file_name}", "r", encoding="utf-8") as data_file:
            data = json.load(data_file)

            for i, build in enumerate(data, start=1):
                new_build = URIRef(NS[f"{role[0].upper() + role[1:]}_Build_{i}"])
                g.add((new_build, RDF.type, NS.Build))

                if role == "killer":
                    g.add((new_build, NS.isInClass, NS.Killer))  # range
                elif role == "survivor":
                    g.add((new_build, NS.isInClass, NS.Survivor))

                for perk in build.get("build"):
                    perk = NS[valid_readable_uri(perk)]
                    g.add((new_build, NS.hasPerk, perk))

                if len(build.get("build")) == 3:
                    perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk4))
                elif len(build.get("build")) == 2:
                    perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk4))
                    perk3 = NS[valid_readable_uri("Third Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk3))
                elif len(build.get("build")) == 1:
                    perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk4))
                    perk3 = NS[valid_readable_uri("Third Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk3))
                    perk2 = NS[valid_readable_uri("Second Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk2))
                elif len(build.get("build")) == 0:
                    perk4 = NS[valid_readable_uri("Fourth Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk4))
                    perk3 = NS[valid_readable_uri("Third Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk3))
                    perk2 = NS[valid_readable_uri("Second Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk2))
                    perk1 = NS[valid_readable_uri("First Empty Slot")]
                    g.add((new_build, NS.hasPerk, perk1))

                g.add((new_build, NS.escapeRate, Literal(float(build.get("escapeRate")), datatype=XSD.float)))
                g.add((new_build, NS.pickRate, Literal(float(build.get("usage")), datatype=XSD.float)))
                g.add((new_build, NS.escapeCount, Literal(int(build.get("escapes")), datatype=XSD.int)))
                g.add((new_build, NS.survivorCount, Literal(int(build.get("survivors")), datatype=XSD.int)))


    add_builds_eg(g2, NS2, "killer")
    add_builds_eg(g2, NS2, "survivor")

    # --------------------- Сохранение

    with open("../ontology/ontology.rdf", "w") as f:
        f.write(g.serialize(format="xml"))

    with open("../ontology/ontology-2.rdf", "w") as f:
        f.write(g2.serialize(format="xml"))

    print("Онтология создана!")
    return g, g2


def create_queries():
    # 1. Лучшие навыки персонажей класса Killer прошлого временного периода
    query1 = """
    PREFIX dbd: <http://www.semanticweb.org/danis/ontologies/2024/12/dead-by-daylight/v1/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
    SELECT DISTINCT ?date ?perk ?escapeRate
    WHERE {
        ?perk a dbd:Perk ;
              dbd:isInClass dbd:Killer ;
              dbd:hasSnapshot ?snapshot .
    
        ?snapshot dbd:date ?date ;
                  dbd:escapeRate ?escapeRate ;
                  dbd:pickRate ?pickRate .
    
        FILTER (?date >= "2024-10-08"^^xsd:date)
        FILTER (?date <= "2024-11-04"^^xsd:date)
        FILTER (?escapeRate < 50.0)
    }
    ORDER BY ASC(?escapeRate)
    LIMIT 10
    """

    # 2. Навыки класса Survivor с Escape Rate < 40% и Pick Rate < 5%
    query2 = """
    PREFIX dbd: <http://www.semanticweb.org/danis/ontologies/2024/12/dead-by-daylight/v1/>
    SELECT DISTINCT ?date ?perk ?escapeRate ?pickRate
    WHERE {
        ?perk dbd:hasSnapshot ?snapshot ;
              dbd:isInClass dbd:Survivor .
        ?snapshot dbd:escapeRate ?escapeRate ;
                  dbd:pickRate ?pickRate ;
                  dbd:date ?date .
        FILTER (?escapeRate < 40.0 && ?pickRate < 5.0)
        FILTER (?date >= "2024-10-08"^^xsd:date)
        FILTER (?date <= "2024-11-04"^^xsd:date)
    }
    LIMIT 10
    """

    return [query1, query2]
    # return [query1, query2, query3, query4, query5, query6]


def execute_query(graph: Graph, query: str):
    return graph.query(query)


def main():

    # ================================================

    import os
    import numpy as np
    import pandas as pd

    from rdflib import Graph

    import tensorflow as tf
    from ampligraph.latent_features import ScoringBasedEmbeddingModel
    from ampligraph.latent_features.loss_functions import get as get_loss
    from ampligraph.latent_features.regularizers import get as get_regularizer
    from ampligraph.evaluation import train_test_split_no_unseen, mr_score, mrr_score, hits_at_n_score

    # ================================================

    DEFAULT_K = 200         # 200
    DEFAULT_EPOCHS = 50     # 100

    # Загружаем граф RDF

    PATH_ONTOLOGY_1 = "../ontology/ontology.rdf"
    PATH_ONTOLOGY_2 = "../ontology/ontology-2.rdf"

    ONTOLOGY_PREFIX_1 = "http://www.semanticweb.org/danis/ontologies/2024/12/dead-by-daylight/v1/"
    ONTOLOGY_PREFIX_2 = "http://www.semanticweb.org/danis/ontologies/2024/12/dead-by-daylight/v2/"

    TEST_DATA_SIZE = 0.2

    g = Graph()
    g1 = Graph()
    g2 = Graph()

    print("Полный граф или усеченная версия? 1/2")
    if os.path.exists(PATH_ONTOLOGY_1) and os.path.exists(PATH_ONTOLOGY_2):
        g = Graph()
        num = input()
        if num == "1":
            g.parse(PATH_ONTOLOGY_1, format="xml")
            g1 += g #
            ONTOLOGY_PREFIX = ONTOLOGY_PREFIX_1
        elif num == "2":
            g.parse(PATH_ONTOLOGY_2, format="xml")
            g1.parse(PATH_ONTOLOGY_1, format="xml") #
            ONTOLOGY_PREFIX = ONTOLOGY_PREFIX_2
        else:
            raise Exception("Ошибочка вышла!")
    else:
        g1, g2 = create_ontology()
        num = input()
        if num == "1":
            g += g1
            ONTOLOGY_PREFIX = ONTOLOGY_PREFIX_1
        elif num == "2":
            g += g2
            ONTOLOGY_PREFIX = ONTOLOGY_PREFIX_2
        else:
            raise Exception("Ошибочка вышла!")


    queries = create_queries()
    for i, query in enumerate(queries):
        print(f"\n--------------- query #{i + 1}")
        result = execute_query(g1, query)
        for i, row in enumerate(result, start=1):
            print(f"{i}. {str(row[1])[len(ONTOLOGY_PREFIX):]}")

    triples = []
    PERKS = []
    BUILDS = []
    SURVIVORS = []
    KILLERS = []
    OTHERS = []

    for s, p, o in g:
        if o.startswith("http") and not o.startswith("http://www.w3.org/"):
            triples.append((str(s), str(p), str(o)))
            # TODO: костыль №4
            o = o[len(ONTOLOGY_PREFIX):]
            s = s[len(ONTOLOGY_PREFIX):]
            if o == "Perk":
                PERKS.append(s)
            elif o == "Build":
                BUILDS.append(s)
            elif o == "Survivor":
                SURVIVORS.append(s)
            elif o == "Killer":
                KILLERS.append(s)
            else:
                OTHERS.append(s)

    PERKS = set(PERKS)
    BUILDS = set(BUILDS)
    SURVIVORS = set(SURVIVORS)
    KILLERS = set(KILLERS)
    OTHERS = set(OTHERS)

    triples = np.array(triples)
    print(f"Всего триплетов для обучения: {len(triples)}")

    X_train, X_test = train_test_split_no_unseen(triples, test_size=round(len(triples) * TEST_DATA_SIZE) if TEST_DATA_SIZE < 1 else TEST_DATA_SIZE, allow_duplication=True)
    print('Train set size:', X_train.shape)
    print('Test set size:', X_test.shape)

    model = ScoringBasedEmbeddingModel(
        k=DEFAULT_K,
        eta=5,
        scoring_type='ComplEx',
        seed=42
    )

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    loss = get_loss('multiclass_nll')
    regularizer = get_regularizer('LP', {'p': 3, 'lambda': 1e-5})

    model.compile(
        optimizer=optimizer,
        loss=loss,
        entity_relation_regularizer=regularizer
    )

    model.fit(
        X_train,
        batch_size=int(X_train.shape[0] / 10),
        epochs=DEFAULT_EPOCHS,
        verbose=True
    )

    ranks = model.evaluate(
        X_test,
        use_filter={'train': X_train, 'test': X_test},
        corrupt_side='s,o',
        verbose=True
    )

    flat_ranks = ranks.flatten()
    valid_ranks = flat_ranks[flat_ranks > 0]

    mr = mr_score(valid_ranks)
    mrr = mrr_score(valid_ranks)
    hits_1 = hits_at_n_score(valid_ranks, n=1)
    hits_3 = hits_at_n_score(valid_ranks, n=3)
    hits_10 = hits_at_n_score(valid_ranks, n=10)

    print()
    print("=========== МЕТРИКИ ===========")
    print(f"MR  (Mean Rank):        {mr:.2f} (чем меньше, тем лучше)")
    print(f"MRR (Mean Reciprocal Rank): {mrr:.3f} (чем ближе к 1, тем лучше)")
    print(f"Hits@1:                {hits_1:.3f}")
    print(f"Hits@3:                {hits_3:.3f}")
    print(f"Hits@10:               {hits_10:.3f}")
    print("===============================\n")

    entities = np.unique(np.concatenate([X_train[:, 0], X_train[:, 2], X_test[:, 0], X_test[:, 2]]))
    entity_embeddings = model.get_embeddings(entities)

    df_emb = pd.DataFrame(entity_embeddings, index=entities)
    df_emb.columns = [f"dim_{i}" for i in range(1, df_emb.shape[1] + 1)]

    df_emb.index = df_emb.index.str.replace(
        ONTOLOGY_PREFIX, "", regex=False
    )

    df_emb.to_csv("../ontology/entity_embeddings.csv", header=False)
    print("Эмбеддинги сущностей сохранены в entity_embeddings.csv")

    print("Готово!")

    # --------------

    DEFAULT_CLUSTERS_AMOUNT = 4

    emb_df = pd.read_csv("../ontology/entity_embeddings.csv", header=None, index_col=0)
    print(emb_df.head())

    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt

    # Применение PCA для снижения размерности
    pca = PCA(n_components=2, random_state=42)
    emb_2d = pca.fit_transform(emb_df.values)

    # Создание DataFrame с результатами
    viz_df = pd.DataFrame(emb_2d, columns=["x", "y"], index=emb_df.index)

    print("Форма после PCA:", viz_df.shape)
    viz_df["cluster"] = KMeans(n_clusters=DEFAULT_CLUSTERS_AMOUNT, random_state=42, n_init=10).fit_predict(emb_df.values)

    # Визуализация по категориям
    viz_df["category"] = "Other"

    # TODO: костыль №5 (относится к №4)
    def get_category(name):
        if name in PERKS:
            return "Perk"
        elif name in BUILDS:
            return "Build"
        elif name in SURVIVORS:
            return "Survivor"
        elif name in KILLERS:
            return "Killer"
        else:
            return "Other"

    viz_df["category"] = viz_df.index.to_series().apply(lambda name: get_category(name))

    category_colors = {
        'Perk': 'blue',
        'Build': 'green',
        'Survivor': 'orange',
        'Killer': 'red',
        'Other': 'black'
    }

    # Визуализация
    plt.figure(figsize=(12, 8))
    for category, color in category_colors.items():
        subset = viz_df[viz_df['category'] == category]
        plt.scatter(subset['x'], subset['y'], label=category, color=color, alpha=0.7)

    # Подписи к точкам
    for idx, row in viz_df.iterrows():
        plt.text(row.x, row.y, str(idx), fontsize=8, alpha=0.7)

    plt.title("Эмбеддинги по категориям")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.legend()
    plt.show()

    # Визуализация кластеров
    plt.figure(figsize=(12, 8))
    for cluster_label in sorted(viz_df["cluster"].unique()):
        cluster_points = viz_df[viz_df["cluster"] == cluster_label]
        plt.scatter(
            cluster_points["x"], cluster_points["y"],
            label=f"Кластер {cluster_label}", alpha=0.6
        )

    # Подписи к точкам
    for idx, row in viz_df.iterrows():
        plt.text(row.x, row.y, str(idx), fontsize=8, alpha=0.7)

    plt.title("Кластеры эмбеддингов")
    plt.xlabel("Dimension 1")
    plt.ylabel("Dimension 2")
    plt.legend()
    plt.show()


if __name__ == '__main__':
    main()
