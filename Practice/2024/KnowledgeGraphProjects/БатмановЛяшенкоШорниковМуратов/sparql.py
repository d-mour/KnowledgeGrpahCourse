import logging
from rdflib import Graph
from rdflib.plugins.sparql import prepareQuery

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# Загрузка графа
GRAPH_FILE = "updated_ontology2.owl"


def load_graph():
    """Загружает граф из файла"""
    g = Graph()
    g.parse(GRAPH_FILE, format="xml")
    return g


# Шаблоны запросов
TEMPLATES = {
    1: """
    PREFIX vg: <http://www.example.org/ontologies/videogames#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?game ?name ?rating ?year ?playtime ?metacritic
    WHERE {
        ?game a vg:PopularGame ;
              vg:has_Genre ?genre ;
              vg:release_Year ?year ;
              vg:rating ?rating ;
              vg:avg_play_time ?playtime ;
              vg:metacritic_score ?metacritic ;
              rdfs:label ?name .
        FILTER (
            ?year > {year} &&
            ?rating > {rating} &&
            ?playtime > {playtime} &&
            ?metacritic > {metacritic} &&
            (?genre IN ({genres}))
        )
    }
    """,
    2: """
    PREFIX vg: <http://www.example.org/ontologies/videogames#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?game ?name ?year ?rating ?playtime
    WHERE {
        ?game rdfs:label ?name ;
              vg:has_Genre ?genre ;
              vg:age_rating "Mature" ;
              vg:avg_play_time ?playtime ;
              vg:rating ?rating ;
              vg:release_Year ?year .
        FILTER (?playtime > {playtime} && ?rating > {rating} && (?genre IN ({genres})))
    }
    """,
    3: """
    PREFIX vg: <http://www.example.org/ontologies/videogames#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?game ?genre ?year ?name ?platform ?playtime ?metacritic
    WHERE {
        ?game a ?subclass .
        ?subclass rdfs:subClassOf vg:{game_mode} .
        ?game vg:has_Genre ?genre .
        ?game vg:release_Year ?year .
        ?game vg:avg_play_time ?playtime .
        ?game vg:metacritic_score ?metacritic .
        ?game vg:has_Platform ?platform .
        OPTIONAL { ?game rdfs:label ?name }
        FILTER (?year > {year})
        FILTER (?playtime > {playtime})
        FILTER (?metacritic > {metacritic})
        FILTER (?platform = vg:PC)
        FILTER (?playtime > 10)
        FILTER (?genre IN ({genres}))
    }
    """
}


# Получение данных от пользователя
def get_user_input(template_id):
    inputs = {}
    genres_list = [
        "Action", "Adventure", "Arcade", "Board Games", "Card", "Casual", "Educational", "Family",
        "Fighting", "Indie", "Massively Multiplayer", "Platformer", "Puzzle", "Racing", "RPG", "Shooter",
        "Simulation", "Sports", "Strategy"
    ]
    game_modes = ["SinglePlayerGame", "MultiplayerGame"]



    if template_id == 1:
        inputs['year'] = int(input("Введите год (например, 2015): ").strip())
        inputs['rating'] = float(input("Введите минимальный рейтинг (например, 4.5): ").strip())
        inputs['playtime'] = int(input("Введите минимальное среднее время игры (например, 40): ").strip())
        inputs['metacritic'] = int(input("Введите минимальный метакритический рейтинг (например, 90): ").strip())
        genres_input = input(f"Введите жанры через запятую из следующего списка: {', '.join(genres_list)}: ").strip()
        inputs['genres'] = ', '.join([f"vg:{genre.strip()}" for genre in genres_input.split(',')])
    elif template_id == 2:
        inputs['playtime'] = int(input("Введите минимальное среднее время игры (например, 10): ").strip())
        inputs['rating'] = float(input("Введите минимальный рейтинг (например, 4): ").strip())
        genres_input = input(f"Введите жанры через запятую из следующего списка: {', '.join(genres_list)}: ").strip()
        inputs['genres'] = ', '.join([f"vg:{genre.strip()}" for genre in genres_input.split(',')])
    elif template_id == 3:
        inputs['year'] = int(input("Введите год выпуска после (например, 2000): ").strip())
        inputs['playtime'] = int(input("Введите минимальное среднее время игры (например, 10): ").strip())
        inputs['metacritic'] = int(input("Введите минимальный метакритический рейтинг (например, 80): ").strip())
        game_mode_input = input(f"Выберите режим игры (SinglePlayerGame или MultiplayerGame): ").strip()
        if game_mode_input not in game_modes:
            print("Неверный режим игры! Выберите либо SinglePlayerGame, либо MultiplayerGame.")
            return None
        inputs['game_mode'] = game_mode_input
        genres_input = input(f"Введите жанры через запятую из следующего списка: {', '.join(genres_list)}: ").strip()
        inputs['genres'] = ', '.join([f"vg:{genre.strip()}" for genre in genres_input.split(',')])
    return inputs


# Формирование SPARQL-запроса
def build_query(template_id, user_inputs):
    query = TEMPLATES[template_id]
    for key, value in user_inputs.items():
        query = query.replace(f"{{{key}}}", str(value))
    return query


# Выполнение запроса
def execute_query(graph, sparql_query):
    try:
        query = prepareQuery(sparql_query)
        results = graph.query(query)
        return [(str(row[0]), str(row[1])) for row in results]
    except Exception as e:
        print(f"Ошибка выполнения запроса: {e}")
        return []


# Основной цикл приложения
def main():
    graph = load_graph()
    print("Добро пожаловать! Выберите шаблон запроса:")
    print("1. Игры с жанрами, рейтингом, метакритиком, временем игры")
    print("2. Игры жанра Action с возрастным рейтингом Mature, минимальным временем игры и рейтингом")
    print(
        "3. Игры с выбранным режимом (SinglePlayerGame или MultiplayerGame), жанром и параметрами времени/метакритика")

    while True:
        try:
            template_id = int(input("Введите номер шаблона (1-3): ").strip())
            if template_id not in TEMPLATES:
                print("Неверный номер шаблона. Попробуйте снова.")
                continue
            user_inputs = get_user_input(template_id)
            if user_inputs is None:
                continue
            sparql_query = build_query(template_id, user_inputs)
            print("Выполняем запрос...")
            results = execute_query(graph, sparql_query)
            if results:
                print("Найдено:")
                for game in results:
                    print(f"Название: {game[1]}")
            else:
                print("Игры по вашему запросу не найдены.")
        except Exception as e:
            print(f"Ошибка: {e}")
        again = input("Хотите выполнить еще один запрос? (да/нет): ").strip().lower()
        if again != 'да':
            print("До свидания!")
            break


if __name__ == "__main__":
    main()
