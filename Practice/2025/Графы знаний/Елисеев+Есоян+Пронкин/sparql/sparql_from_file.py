from rdflib import Graph, Namespace
from rdflib.plugins.sparql import prepareQuery
import time
import os

# Параметры
RDF_FILE = "../tmdb_data.ttl"
SPARQL_INPUT_FILE = "sparql_input.sparql"


def load_graph(file_path: str) -> Graph:
    print(f"Загрузка RDF графа из '{file_path}'...")
    g = Graph()
    g.parse(file_path, format="turtle")
    print(f"Граф загружен. Количество триплетов: {len(g):,}")
    return g


def setup_namespace(graph: Graph) -> Namespace:
    fr_namespace = "http://example.org/film-rating#"
    fr = Namespace(fr_namespace)
    graph.bind("fr", fr)
    graph.bind("rdf", Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#"))
    graph.bind("rdfs", Namespace("http://www.w3.org/2000/01/rdf-schema#"))
    graph.bind("xsd", Namespace("http://www.w3.org/2001/XMLSchema#"))
    return fr


def build_prefixes(fr: Namespace) -> str:
    return f"""
        PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl:  <http://www.w3.org/2002/07/owl#>
        PREFIX fr:   <{fr}>
        PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>
    """.strip() + "\n\n"


def read_query_from_file(file_path: str) -> str:
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл с запросом '{file_path}' не найден")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read().strip()

    if not content:
        raise ValueError(f"Файл '{file_path}' пустой")

    return content


def maybe_add_prefixes(raw_query: str, prefixes: str) -> str:
    lowered = raw_query.lower()
    if "prefix " in lowered:
        return raw_query  # пользователь сам указал префиксы
    return prefixes + raw_query


def execute_query(graph: Graph, query: str, query_name: str = "Пользовательский запрос"):
    print("\n" + "=" * 60)
    print(f"{query_name}")
    print("=" * 60)

    start_time = time.time()
    try:
        prepared = prepareQuery(query)
        results = graph.query(prepared)
        elapsed = time.time() - start_time
        print(f"Время выполнения: {elapsed:.2f} сек")

        if len(results) == 0:
            print("Результатов не найдено")
            return

        print("\nРезультаты:")
        print("-" * 80)

        rows = list(results)

        col_widths = [0] * len(rows[0])
        for row in rows:
            for i, val in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(val)))

        for i, var in enumerate(results.vars):
            print(f"{var:<{col_widths[i]}}", end="  ")
        print()
        print("-" * sum(col_widths) + "--" * len(col_widths))

        for row in rows:
            for i, val in enumerate(row):
                print(f"{val:<{col_widths[i]}}", end="  ")
            print()

        print(f"\nНайдено записей: {len(rows)}")

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"Ошибка при выполнении запроса (время: {elapsed:.2f} сек): {e}")


if __name__ == "__main__":
    try:
        graph = load_graph(RDF_FILE)
        fr = setup_namespace(graph)
        prefixes = build_prefixes(fr)

        print(f"Используем пространство имён fr: {fr}")
        print(f"Файл с запросом: '{SPARQL_INPUT_FILE}'")
        print("\nИнтерактивный режим.")
        print("Редактируйте sparql_input.sparql в редакторе, затем:")
        print("  - Нажмите Enter, чтобы выполнить текущий запрос")
        print("  - Введите q и Enter, чтобы выйти\n")

        while True:
            cmd = input("Нажмите Enter для выполнения запроса (q для выхода): ").strip().lower()
            if cmd in {"q", "quit", "exit"}:
                print("Выход.")
                break

            try:
                raw_query = read_query_from_file(SPARQL_INPUT_FILE)
                full_query = maybe_add_prefixes(raw_query, prefixes)
                execute_query(graph, full_query, "Запрос из файла sparql_input.sparql")
            except Exception as e:
                print(f"– Ошибка при чтении/выполнении запроса: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 60)
        print("ВЫПОЛНЕНИЕ ЗАВЕРШЕНО")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"– Ошибка: {e}")
        print("  Укажите правильный путь к RDF/или SPARQL файлам.")
    except Exception as e:
        print(f"– Непредвиденная ошибка при инициализации: {e}")
        import traceback
        traceback.print_exc()
