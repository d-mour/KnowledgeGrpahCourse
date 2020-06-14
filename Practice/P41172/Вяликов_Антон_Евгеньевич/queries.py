from rdflib import Graph, Literal, RDF, URIRef
import requests


graph = Graph()
graph.parse("AftermarketPartsOntologyFull.owl", format='turtle')

print("Graph has {} statements.".format(len(graph)))

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/avyal/ontologies/2020/5/untitled-ontology-3#>
    SELECT ?body ?price
    WHERE {
        ?body a ns1:Bumpers;
                ns1:hasManufacturer ns1:C-West; 
                ns1:hasPrice ?price .
    }""")

print('\n$$ C-West bumpers with price $$')
for row in res:
    print(row[0].split('#')[1], row[1])

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/avyal/ontologies/2020/5/untitled-ontology-3#>
    SELECT ?manufacturer ?body ?price
    WHERE {
        ?body a ns1:Body_kits;
                ns1:compatibleWithCar "Mazda RX-7 FD3S";
                ns1:hasManufacturer ?manufacturer;
                ns1:hasPrice ?price .
    }""")

print('\n$$ Body kits for Mazda RX-7 FD3S with price $$')
for row in res:
    print(row[0].split('#')[1], row[1].split('#')[1], row[2])

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/avyal/ontologies/2020/5/untitled-ontology-3#>
    SELECT  ?manufacturer ?wheels ?speed ?price
    WHERE {
        ?wheels a ns1:Tires;
                  ns1:forPublicRoad true;
                  ns1:hasManufacturer ?manufacturer;
                  ns1:hasMaxSpeed ?speed .
    }""")

print('\n$$ Road tires with max speed$$')
for row in res:
    print(row[0].split('#')[1], row[1].split('#')[1], row[2])

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/avyal/ontologies/2020/5/untitled-ontology-3#>
    SELECT ?manufacturer ?wheels  ?price
    WHERE {
        ?wheels a ns1:Rims;
                  ns1:hasPrice ?price;
                  ns1:hasManufacturer ?manufacturer;
                  ns1:hasSize ?size .
        FILTER(?size > 19)
    }""")

print('\n$$ Rims, bigger than 19 inch $$')
for row in res:
    print(row[0].split('#')[1], row[1].split('#')[1], row[2])

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/avyal/ontologies/2020/5/untitled-ontology-3#>
    SELECT ?manufacturer ?part ?price
    WHERE {
        ?part a ns1:Clutches;
                  ns1:hasMaterial "Ceramic";
                  ns1:hasManufacturer ?manufacturer;
                  ns1:hasPrice ?price .
    }""")

print('\n$$ Ceramic clutches with price $$')
for row in res:
    print(row[0].split('#')[1], row[1].split('#')[1], row[2])
