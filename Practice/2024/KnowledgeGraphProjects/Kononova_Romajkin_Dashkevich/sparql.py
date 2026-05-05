from rdflib import Graph, Namespace

base_uri = "http://www.semanticweb.org/liessa/ontologies/2024/10/untitled-ontology-5"
n = Namespace(base_uri)

graph = Graph()
graph.parse("Zzzzz.rdf", format="xml")

# Запрос 1: Кто основал Винтерфелл?
query1 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX got: <http://www.semanticweb.org/liessa/ontologies/2024/10/untitled-ontology-5#>
SELECT ?ruler
	WHERE { 
got:Винтерфелл got:Владелец ?ruler .
 }
"""
print('\n FIRST QUERY\n')
results1 = graph.query(query1)
for row in results1:
    print(f"Ruler: {row['ruler']}")

# Запрос 2: Какое население у Королевства который основал Брандон Строитель?
query2 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX got: <http://www.semanticweb.org/liessa/ontologies/2024/10/untitled-ontology-5#>
SELECT ?population
	WHERE { 
?kingdom a got:Королевства .
?kingdom got:Владелец got:Брандон_Строитель .
?kingdom got:Население ?population
 }
"""
print('\n SECOND QUERY\n')

results2 = graph.query(query2)
for row in results2:
    print(f"Population: {row['population']}")

# Запрос 3: Все представители Старков
query3 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX got: <http://www.semanticweb.org/liessa/ontologies/2024/10/untitled-ontology-5#>
SELECT ?ruler
	WHERE { 
?ruler got:Принадлежность got:Старки .
 }
"""
print('\n THIRD QUERY\n')

results3 = graph.query(query3)
for row in results3:
    print(f"Stark: {row['ruler']}")

# Запрос 4: Какой девиз у дома к которому пренадлежит Эйгон 1?
query4 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX got: <http://www.semanticweb.org/liessa/ontologies/2024/10/untitled-ontology-5#>
SELECT ?creed
	WHERE { 
got:Эйгон_1_Таргариен got:Принадлежность ?house .
?house got:Девиз ?creed .
 }
"""
print('\n FOURTH QUERY\n')

results4 = graph.query(query4)
for row in results4:
    print(f"Creed: {row['creed']}")

query5 = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX got: <http://www.semanticweb.org/liessa/ontologies/2024/10/untitled-ontology-5#>
SELECT ?kingdom ?population
	WHERE { 
?kingdom a got:Королевства.
?kingdom got:Население ?population.
 }
ORDER BY DESC(?population)
"""
print('\n FIFTH QUERY\n')
results5 = graph.query(query5)
for row in results5:
    print(f"Kingdom: {row['kingdom']}, Population: {row['population']}")
