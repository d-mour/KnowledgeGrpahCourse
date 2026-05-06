from rdflib import Graph

g = Graph()
g.parse("roblox_graph.ttl", format="turtle")

# Посмотреть все катастрофы
query = """
PREFIX ex: <http://example.org/roblox/>
SELECT DISTINCT ?disaster ?label
WHERE {
  ?disaster a ex:Disaster .
  OPTIONAL { ?disaster ex:hasLabel ?label . }
}
"""

for row in g.query(query):
    print("Disaster:", row.disaster, "| label:", row.label)

# Найти всех игроков из текстовой разметки
query = """
PREFIX ex: <http://example.org/roblox/>
SELECT DISTINCT ?player ?name
WHERE {
  ?ann a ex:TextAnnotation ;
       ex:mentionsPlayer ?player .
  ?player ex:hasLabel ?name .
}
ORDER BY ?name
"""

for row in g.query(query):
    print("Player:", row.name)
