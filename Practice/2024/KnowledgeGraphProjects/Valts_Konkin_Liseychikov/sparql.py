from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, OWL, XSD
import pandas as pd

# Параметры
UPDATED_RDF_FILE = 'updated_movies.rdf'  # файл для сохранения результата


# Загрузка RDF графа
def load_graph(file_path):
    g: Graph = Graph()
    g.parse(file_path, format='xml')
    return g


# Настройка пространства имен
def setup_namespace(graph):
    base_namespace = "http://www.semanticweb.org/martin/ontologies/2024/9/untitled-ontology-6/"
    ns = Namespace(base_namespace)
    graph.bind('ns', ns)
    return ns


# Загрузка данных из CSV
def load_csv(file_path):
    return pd.read_csv(file_path)


# Выполнение SPARQL-запросов
def execute_query(graph, query):
    print("Executing query...")
    results = graph.query(query)
    for row in results:
        print(row)


# Примеры SPARQL-запросов
def sparql_queries(graph, ns):
    # 1. Какие фильмы с актером X имеют рейтинг не ниже фильма Y?
    query_1 = f"""
        PREFIX ns: <{ns}>
        SELECT ?film 
        WHERE {{
          ?film ns:hasActor <{ns}Actor/RyanGosling> .
          ?film ns:rating ?rating .
          <{ns}film/Searching> ns:rating ?ratingY .
          FILTER(?rating >= ?ratingY)
        }}
        """
    print("\nQuery 1 Results:")
    execute_query(graph, query_1)

    # 2. Какие фильмы с актерами X срежиссировал Y?
    query_2 = f"""
        PREFIX ns: <{ns}>
        SELECT ?film 
        WHERE {{
          ?film ns:hasActor <{ns}Actor/RyanGosling> .
          ?film ns:hasDirector <{ns}Director/NicolasWindingRefn> .
        }}
        """
    print("\nQuery 2 Results:")
    execute_query(graph, query_2)

    # 3. В каких фильмах снимался актер X, после фильма Y?
    query_3 = f"""
        PREFIX ns: <{ns}>
        SELECT ?film 
        WHERE {{
          ?film ns:hasActor <{ns}Actor/RyanGosling> .
          ?film ns:release_year ?releaseDate .
          <{ns}film/Drive> ns:release_year ?releaseDateY .
          FILTER(?releaseDate >= ?releaseDateY)
        }}
        """
    print("\nQuery 3 Results:")
    execute_query(graph, query_3)

    # 4. Какие фильмы снимал X, которые не длятся не дольше Y и имеют рейтинг не ниже Z?
    query_4 = f"""
        PREFIX ns: <{ns}>
        SELECT ?film 
        WHERE {{
          ?film ns:hasDirector <{ns}Director/SatoshiKon> .
          ?film ns:duration ?duration .
          ?film ns:rating ?rating .
        }}
        """
    print("\nQuery 4 Results:")
    execute_query(graph, query_4)

    # 5. Какие фильмы, в жанре X, были сняты Y?
    query_5 = f"""
        PREFIX ns: <{ns}>
    SELECT ?film 
    WHERE {{
      ?film ns:hasCategory <{ns}Category/Comedy> .
      ?film ns:hasDirector <{ns}Director/GuyRitchie> .
    }}
        """
    print("\nQuery 5 Results:")
    execute_query(graph, query_5)


# Главный скрипт
if __name__ == "__main__":
    # Загрузка RDF графа
    graph = load_graph(UPDATED_RDF_FILE)

    # Настройка пространства имен
    ns = "http://www.semanticweb.org/martin/ontologies/2024/9/untitled-ontology-6/"

    # Выполнение SPARQL-запросов
    sparql_queries(graph, ns)