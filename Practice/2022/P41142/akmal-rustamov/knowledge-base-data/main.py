from data_importer import fill_graph
from sparql_requester import run_queries

ONTOLOGY = "../wine.rdf"
EXTRACTED_DATA = "../data"
ONTOLOGY_FORMAT = "rdf"

if __name__ == '__main__':
    fill_graph(ONTOLOGY, ONTOLOGY_FORMAT, EXTRACTED_DATA, "./")

    run_queries(ONTOLOGY, ONTOLOGY_FORMAT)
