
from rdflib import Graph, Namespace, URIRef, XSD, Literal
from rdflib.namespace import RDF, OWL
import pandas as pd

# Параметры
RDF_FILE = 'movies_woth_properties.rdf'  # исходный RDF файл
CSV_FILE = 'IMDb_Data_final.csv'  # CSV с данными
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

    # Указание классов и объектных свойств
    classes = ['Actor', 'Director', 'Category', 'film']
    for cls in classes:
        graph.add((URIRef(f"{ns}{cls}"), RDF.type, OWL.Class))

    object_properties = ['longer', 'older', 'higher_rating', 'hasActor', 'hasDirector', 'hasCategory']
    data_properties = ['duration', 'release_year', 'rating']

    for prop in object_properties:
        prop_uri = URIRef(f"{ns}{prop}")
        graph.add((prop_uri, RDF.type, OWL.ObjectProperty))

    for prop in data_properties:
        prop_uri = URIRef(f"{ns}{prop}")
        graph.add((prop_uri, RDF.type, OWL.DatatypeProperty))

    return ns


# Загрузка данных из CSV
def load_csv(file_path):
    return pd.read_csv(file_path)


# Создание или поиск URI для сущности
def get_or_create_entity(graph, ns, entity_type, value):
    entity_uri = URIRef(f"{ns}{entity_type}/{value.replace(' ', '_')}")
    if (entity_uri, RDF.type, ns[entity_type]) not in graph:
        graph.add((entity_uri, RDF.type, ns[entity_type]))
    return entity_uri


# Создание или поиск URI для фильма
def get_or_create_film(graph, ns, title):
    return get_or_create_entity(graph, ns, 'film', title)


# Добавление данных фильма в граф
def add_movie_data(graph, ns, row, film_uris):
    if 'Paris, ' in row['Title']:
        print(row['Title'])
        exit()
    title_ = row['Title'].replace('"', '')
    movie_uri = get_or_create_film(graph, ns, title_)
    film_uris[title_] = {
        'uri': movie_uri,
        'duration': int(row['Duration'].split()[0][:-3]),  # Извлекаем числовое значение длительности
        'release_year': int(row['ReleaseYear']),
        'rating': float(row['IMDb-Rating'])
    }

    graph.add((movie_uri, ns.release_year, Literal(row['ReleaseYear'], datatype=XSD.integer)))
    graph.add((movie_uri, ns.duration, Literal(row['Duration'].split()[0][:-3], datatype=XSD.integer)))
    graph.add((movie_uri, ns.rating, Literal(row['IMDb-Rating'], datatype=XSD.float)))

    # Актеры
    actors = row['Stars'].split(',')
    for actor in actors:
        actor = actor.strip().replace('"', '')
        if actor == "" or actor is None: continue

        actor_uri = get_or_create_entity(graph, ns, 'Actor', actor)
        graph.add((movie_uri, ns.hasActor, actor_uri))

    # Режиссеры
    director = row['Director'].split(',')[0].replace('"', "")
    director_uri = get_or_create_entity(graph, ns, 'Director', director)
    graph.add((movie_uri, ns.hasDirector, director_uri))

    # Жанры
    genres = row['Category'].split(',')
    for genre in genres:
        genre = genre.strip().replace('"', '')
        if genre == "" or genre is None: continue

        category_uri = get_or_create_entity(graph, ns, 'Category', genre)
        graph.add((movie_uri, ns.hasCategory, category_uri))

    return movie_uri


# Добавление сравнительных связей
def add_comparative_relations(graph: Graph, ns, film_uris):
    films = list(film_uris.values())
    for i, film1 in enumerate(films):
        for j, film2 in enumerate(films):
            if i != j:
                # Добавление связи longer
                if film1['duration'] > film2['duration']:
                    graph.add((film1['uri'], ns.longer, film2['uri']))
                # Добавление связи older
                if film1['release_year'] < film2['release_year']:
                    graph.add((film1['uri'], ns.older, film2['uri']))
                # Добавление связи higher_rating
                if film1['rating'] > film2['rating']:
                    graph.add((film1['uri'], ns.higher_rating, film2['uri']))


# Обновление графа данными из CSV
def update_graph_with_csv(graph, csv_data, ns):
    film_uris = {}
    for _, row in csv_data.iterrows():
        add_movie_data(graph, ns, row, film_uris)
    add_comparative_relations(graph, ns, film_uris)


# Сохранение обновленного графа
def save_graph(graph, file_path):
    graph.serialize(destination=file_path, format='xml')


# Главный скрипт
if __name__ == "__main__":
    # Загрузка RDF графа
    graph = load_graph(RDF_FILE)

    # Настройка пространства имен
    ns = setup_namespace(graph)

    # Загрузка данных из CSV
    csv_data = load_csv(CSV_FILE)

    # Обновление графа данными из CSV
    update_graph_with_csv(graph, csv_data, ns)

    # Сохранение обновленного графа
    save_graph(graph, UPDATED_RDF_FILE)
    print(f"Обновленный RDF граф сохранен в файл: {UPDATED_RDF_FILE}")
