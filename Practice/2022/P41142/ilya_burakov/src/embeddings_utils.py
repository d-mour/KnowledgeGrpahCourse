import logging
import pickle
from pathlib import Path
from typing import Union

from rdflib import Graph, URIRef, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_graph

from node2vec import Node2Vec

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(name)s[%(process)d] - %(threadName)s - %(levelname)s - %(message)s")
logging.getLogger("numba").setLevel(logging.INFO)

embeddings = Path("../embeddings")
ontologies = Path("../ontologies")
embeddings.mkdir(exist_ok=True)


def _node_to_nx_key(node: Union[URIRef, Literal]):
    return str(node)


def load_graph(path):
    logging.info(f"Loading rdflib graph from {path}")
    g = Graph()
    g.parse(path, format="turtle")
    logging.info(f"Converting graph of {len(g)} triples to networkx")
    ng = rdflib_to_networkx_graph(g, transform_s=_node_to_nx_key, transform_o=_node_to_nx_key)
    return ng


def load_walks(path):
    logging.info(f"Loading walks from {path}")
    with path.open("rb") as f:
        return pickle.load(f)

