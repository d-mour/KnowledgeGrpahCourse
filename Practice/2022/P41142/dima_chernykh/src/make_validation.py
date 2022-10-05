from pyshacl import validate
from rdflib import Graph

graph = Graph().parse("../pokemons_cut.owl", format='json-ld')


def execute():
    result = validate(graph,
                 inference='rdfs',
                 abort_on_first=False,
                 allow_infos=False,
                 allow_warnings=False,
                 meta_shacl=False,
                 advanced=False,
                 js=False,
                 debug=False)
    print(result)


execute()