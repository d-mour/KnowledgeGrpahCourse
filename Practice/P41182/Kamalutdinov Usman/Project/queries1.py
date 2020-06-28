from rdflib import Graph, Literal, RDF, URIRef
import requests


graph = Graph()
graph.parse("new.owl", format='turtle')

print("Graph has {} statements.".format(len(graph)))

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/fairytail/ontologies/2020/4/kia#>
    SELECT ?model ?complectation ?price
    WHERE {
       ?model a ns1:Ceed;
                ns1:has_complectation ?complectation;
                p0:has_price ?price .
       FILTER(?price < 1300000)
    }""")
print('\n$$ complectations with price $$')
for row in res:
    print(row[0].split('/')[7], row[1].split('/')[7], row[2])

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/fairytail/ontologies/2020/4/kia#>
    SELECT ?model ?price
    WHERE {
       ?model a ns1:Stinger; 
                ns1:has_drive ns1:rear;
                p0:has_price ?price .
    }""")
print('\n$$ rear with price $$')
for row in res:
    print(row[0].split('/')[7], row[1])

res = graph.query(
    """PREFIX : <http://www.semanticweb.org/fairytail/ontologies/2020/4/kia#>
    SELECT ?model ?complectation ?price
    WHERE {
       ?model a ns1:Mohave;
                ns1:has_type ns1:Crossover_and_SUV;
                ns1:has_drive ns1:front;
                ns1:has_complectation ?complectation;
                p0:has_price ?price .
       FILTER(?price < 3000000)
    }""")
print('\n$$ SUV $$')
for row in res:
    print(row[0].split('/')[7], row[1].split('/')[7], row[2])

