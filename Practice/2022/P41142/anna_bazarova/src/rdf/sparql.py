from rdflib import Graph


def make_sparql_req():
    g = Graph().parse("./src/resources/graph_resaved.owl")

    # Query the data in g using SPARQL
    print("1) За каких существ дают больше 1000, но меньше 2000 опыта?")
    q = """
        PREFIX base: <http://www.semanticweb.org/annab/ontologies/2022/3/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?Beast
        WHERE { 
            ?Beast a base:Beast;
                base:hasXPValue ?xp .
            FILTER(?xp < xsd:integer(2000) && ?xp > xsd:integer(1000))
        }
    """

    # Apply the query to the graph and iterate through results
    for r in g.query(q):
        print(r)

    # Query the data in g using SPARQL
    print("2) У каких существ сила и ловкость больше 20?")
    q = """
        PREFIX base: <http://www.semanticweb.org/annab/ontologies/2022/3/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?Beast
        WHERE { 
            ?Beast a base:Beast;
                base:str ?str;
                base:dex ?dex .
            FILTER(?str > xsd:integer(20) && ?dex > xsd:integer(20))
        }
    """

    # Apply the query to the graph and iterate through results
    for r in g.query(q):
        print(r)

    # Query the data in g using SPARQL
    print("3) Какие монстры говорят по-русски?")
    q = """
        PREFIX base: <http://www.semanticweb.org/annab/ontologies/2022/3/ontology#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        SELECT ?Beast
        WHERE { 
            ?Beast a base:Beast;
                base:hasLanguages ?lang .
                
            FILTER(?lang = base:RussianL)
        }
    """

    # Apply the query to the graph and iterate through results
    for r in g.query(q):
        print(r)

    # Query the data in g using SPARQL
    print("4) Какое злое существо говорит на селестиале?")
    q = """
            PREFIX base: <http://www.semanticweb.org/annab/ontologies/2022/3/ontology#>
            PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

            SELECT ?Beast
            WHERE { 
                ?Beast a base:Beast;
                    base:hasAlignment ?alig;
                    base:hasLanguages ?lang .
                FILTER((?alig = base:chaoticEvil || ?alig = base:neutralEvil || ?alig = base:lawfulEvil) && ?lang = base:CelestialL)
            }
        """

    # Apply the query to the graph and iterate through results
    for r in g.query(q):
        print(r)
