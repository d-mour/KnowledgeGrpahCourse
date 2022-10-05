import rdflib
from rdflib import URIRef
from rdflib.void import generateVoID

graph = rdflib.Graph()
graph.parse('../pokemons_cut.owl', format='json-ld')

void_graph, d = generateVoID(graph, dataset=URIRef('http://www.semanticweb.org/markus/ontologies/2022/9/pokemon/dataset'))
void_graph.serialize(destination='../pokemons_cut_void.owl', format='json-ld')