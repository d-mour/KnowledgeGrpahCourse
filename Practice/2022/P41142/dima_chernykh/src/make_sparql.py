from rdflib import Graph
graph = Graph().parse("../pokemons_cut.owl", format='json-ld')

def make_sparql_request():
    print("\n1) Топ 10 высоких покемонов")
    q = """
        PREFIX base: <http://www.semanticweb.org/markus/ontologies/2022/9/pokemon#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?Pokemon
        WHERE { 
            ?Pokemon a base:Pokemon ;
                     base:height ?Height .
        }
        ORDER BY DESC(?Height)
        LIMIT 10
    """

    for r in graph.query(q):
        print(r)

    print("\n2) У каких покемонов сила и защита больше 100?")
    q = """
        PREFIX base: <http://www.semanticweb.org/markus/ontologies/2022/9/pokemon#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?Pokemon ?attack ?defence
        WHERE { 
            ?Pokemon a base:Pokemon;
                base:attack ?attack ;
                base:defense ?defense .
            FILTER(?attack > xsd:integer(100) && ?defense > xsd:integer(100))
        }
    """

    for r in graph.query(q):
        print(r)

    print("\n3) Какие покемоны не получают урон от монстров и движений типа дракона?")
    q = """
        PREFIX base: <http://www.semanticweb.org/markus/ontologies/2022/9/pokemon#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        SELECT ?Pokemon
        WHERE { 
            ?Pokemon a base:Pokemon ;
                base:hasPokemonType ?type1 .
            ?type1 base:hasNoDamageFrom ?type2 .
            FILTER(?type2 = base:dragon-type)
        }
    """

    for r in graph.query(q):
        print(r)

    print('\n4) Какой двухтипный покемон может выучить движение водопад, имея свыше 100 очков здоровья?')
    q = """
            PREFIX base: <http://www.semanticweb.org/markus/ontologies/2022/9/pokemon#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
            SELECT DISTINCT ?Pokemon
            WHERE { 
                ?Pokemon a base:Pokemon;
                    base:hasPokemonType ?type1, ?type2 ;
                    base:canLearn ?move ;
                    base:hp ?hp .
                FILTER((?type1 != ?type2) && (?move = base:waterfall-move) && (?hp > xsd:integer(100))).
            }
        """

    for r in graph.query(q):
        print(r)


def execute():
    make_sparql_request()


execute()