from rdflib import Graph, Namespace
from rdflib.namespace import RDF

# Загрузка RDF-данных
file_path = 'skins.rdf'
g = Graph()
g.parse(file_path, format='xml')

# Определение пространства имен
SKIN = Namespace("http://example.org/skin#")

# Функция для выполнения SPARQL-запросов
def execute_query(graph, query):
    results = graph.query(query)
    for row in results:
        print(row)

# Обновленные запросы
query_1 = """
PREFIX skin: <http://example.org/skin#>
SELECT (COUNT(?item) AS ?count) (COUNT(?above1000) AS ?countAbove1000)
WHERE {
    ?item skin:hasOffer ?offer .
    ?offer skin:price ?price .
    FILTER (?price > 1000)
}
"""

query_2 = """
PREFIX skin: <http://example.org/skin#>
SELECT ?item
WHERE {
    ?item skin:hasHistory ?history .
    ?history skin:price ?price .
    FILTER (?price < 100)  # Пример фильтрации для анализа цен
}
LIMIT 20
"""

query_3 = """
PREFIX skin: <http://example.org/skin#>
SELECT ?item (COUNT(?history) AS ?popularity)
WHERE {
    ?item skin:hasHistory ?history .
}
GROUP BY ?item
ORDER BY DESC(?popularity)
LIMIT 5
"""

query_4 = """
PREFIX skin: <http://example.org/skin#>
SELECT (COUNT(?offer) AS ?totalOffers) (COUNT(?belowAverage) AS ?belowAverageOffers)
WHERE {
    ?offer skin:price ?price .
    FILTER (?price < 50)  # Пример фильтрации для недорогих предложений
}
"""

query_5 = """
PREFIX skin: <http://example.org/skin#>
SELECT ?item ?price
WHERE {
    ?item skin:hasOffer ?offer .
    ?item skin:collection ?collection .
    ?offer skin:price ?price .
    FILTER (?collection = "Фальшион" && ?price > 50)
}
LIMIT 20
"""

print("\n1. Частота превышения цены 1000 долларов")
execute_query(g, query_1)

print("\n2. Скины с ценой ниже 100")
execute_query(g, query_2)

print("\n3. Популярные скины (по истории)")
execute_query(g, query_3)

print("\n4. Процент предложений с ценой ниже 50")
execute_query(g, query_4)

print("\n5. AWP из коллекции Фальшион")
execute_query(g, query_5)
