import sys
from datetime import datetime

from rdflib import Graph

ONTO_FILE = "alchemy_full.rdf"
RESULT_FILE = "results.txt"


def log_print(*args, **kwargs):
    """
    Выводит текст в консоль И записывает его в файл
    """
    try:
        with open(RESULT_FILE, "a", encoding="utf-8") as f:
            print(*args, **kwargs, file=f)
    except Exception as e:
        sys.stderr.write(f"Ошибка записи в файл: {e}\n")


def log_header(title):
    """Пишет красивый заголовок с датой в файл перед запросом"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"\n{'=' * 20}\n ЗАПРОС: {title}\n ВРЕМЯ: {timestamp}\n{'=' * 20}"
    log_print(header)


def load_graph(file_path):
    print(f"Загрузка онтологии из {file_path}...")
    try:
        g = Graph()
        g.parse(file_path, format="xml")
        print("Онтология успешно загружена!")
        return g
    except FileNotFoundError:
        print(f"Ошибка: Файл '{file_path}' не найден.")
        sys.exit(1)
    except Exception as e:
        print(f"Ошибка при чтении файла: {e}")
        sys.exit(1)


def query_uses_element(g: Graph, element_name: str):
    q = f"""
    PREFIX ex: <http://example.org/alchemy#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?recipeLabel ?resultLabel
    WHERE {{
      ?ingredient rdfs:label "{element_name}"@ru .
      ?recipe ex:hasIngredient ?ingredient ;
              ex:hasResult ?result ;
              rdfs:label ?recipeLabel .
      ?result rdfs:label ?resultLabel .
    }}
    """
    results = g.query(q)
    if not results:
        print(f"\n[INFO] Элемент '{element_name}' не используется ни в одном рецепте.")
        return

    print(f"\n--- Рецепты с использованием '{element_name}' ---")
    for row in results:
        print(f"• Рецепт: {row.recipeLabel}  -->  Итог: {row.resultLabel}")


def query_check_basic_craft(g: Graph, element_name: str):
    q = f"""
    PREFIX ex: <http://example.org/alchemy#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?status ?recipeLabel ?resultElement
    WHERE {{
      {{
        BIND("{element_name}"@ru AS ?targetName)
        ?recipe ex:hasResult ?res ; rdfs:label ?recipeLabel .
        ?res rdfs:label ?targetName .
        FILTER NOT EXISTS {{
          ?recipe ex:hasIngredient ?ing .
          FILTER NOT EXISTS {{ ?ing a ex:BasicElement }}
        }}
        BIND("FOUND" AS ?status)
        BIND(?targetName AS ?resultElement)
      }}
      UNION
      {{
        ?recipe2 ex:hasResult ?res2 ; rdfs:label ?recipeLabel .
        ?res2 rdfs:label ?resultElement .
        FILTER NOT EXISTS {{
          ?recipe2 ex:hasIngredient ?ing2 .
          FILTER NOT EXISTS {{ ?ing2 a ex:BasicElement }}
        }}
        BIND("LIST" AS ?status)
      }}
    }}
    ORDER BY ?status
    """
    results = g.query(q)

    found = False
    possible = []

    for row in results:
        if str(row.status) == "FOUND":
            found = True
            print(f"\n[ДА] '{element_name}' создается из базовых: {row.recipeLabel}")
            return
        else:
            possible.append(f"{row.resultElement} ({row.recipeLabel})")

    print(f"\n[НЕТ] '{element_name}' нельзя создать только из базовых в 1 шаг.")
    print("Список возможных рецептов из базовых элементов:")
    for p in possible:
        print(f" - {p}")


def query_reachable_iterative(g: Graph, start_element: str, max_steps: int):
    log_header(f"Цепочки от '{start_element}' на {max_steps} шагов")
    log_print(f"\n--- Поиск... ---")

    found_results = {}
    current_layer_items = [(start_element, [])]

    for step in range(1, max_steps + 1):
        next_layer_items = []
        unique_names = set(name for name, _ in current_layer_items)
        step_cache = {}

        for item_name in unique_names:
            q = f"""
            PREFIX ex: <http://example.org/alchemy#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            SELECT ?resLabel ?recipeLabel WHERE {{
                ?ing rdfs:label "{item_name}"@ru .
                ?recipe ex:hasIngredient ?ing ;
                        ex:hasResult ?res ;
                        rdfs:label ?recipeLabel .
                ?res rdfs:label ?resLabel .
            }}
            """
            res = g.query(q)
            step_cache[item_name] = []
            for row in res:
                step_cache[item_name].append((str(row.resLabel), str(row.recipeLabel)))

        for item_name, history in current_layer_items:
            if item_name in step_cache:
                for res_label, recipe_label in step_cache[item_name]:
                    new_step_desc = f"Шаг {step}: {recipe_label}"
                    new_history = history + [new_step_desc]

                    if res_label not in found_results:
                        found_results[res_label] = new_history
                        next_layer_items.append((res_label, new_history))

        if not next_layer_items:
            break

        current_layer_items = next_layer_items

    if not found_results:
        log_print("Ничего нового создать не удалось.")
        return

    i = 1
    for res_name, history in found_results.items():
        log_print(f"\n{i}. {res_name}")
        for line in history:
            log_print(f"   {line}")
        i += 1


def query_crafting_tree(g: Graph, target_element: str):
    q = f"""
    PREFIX ex: <http://example.org/alchemy#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

    SELECT ?stepResultLabel ?recipeLabel (GROUP_CONCAT(?ingLabel; separator=", ") AS ?ingredients) ?dist
    WHERE {{
      BIND("{target_element}"@ru AS ?targetName)
      ?target rdfs:label ?targetName .

      ?target (^ex:hasResult / ex:hasIngredient)* ?component .

      ?recipe ex:hasResult ?component .
      ?recipe rdfs:label ?recipeLabel .
      ?component rdfs:label ?stepResultLabel .

      ?recipe ex:hasIngredient ?ing .
      ?ing rdfs:label ?ingLabel .

      {{
        SELECT ?component (COUNT(?mid) AS ?dist)
        WHERE {{
            BIND("{target_element}"@ru AS ?targetName)
            ?target rdfs:label ?targetName .

            ?target (^ex:hasResult / ex:hasIngredient)* ?mid .
            ?mid (^ex:hasResult / ex:hasIngredient)* ?component .
        }}
        GROUP BY ?component
      }}
    }}
    GROUP BY ?stepResultLabel ?recipeLabel ?dist
    ORDER BY DESC(?dist)
    """

    results = g.query(q)

    if not results:
        print(f"\n[INFO] Не найден рецепт для '{target_element}' или это базовый элемент.")
        return

    print(f"\n=== ГАЙД ПО СОЗДАНИЮ: '{target_element}' ===")
    print("Следуйте шагам сверху вниз:")
    print("-" * 85)
    print(f"{'ШАГ':<4} | {'СОЗДАЕМ':<20} | {'ИЗ ЧЕГО (ИНГРЕДИЕНТЫ)':<30} | {'РЕЦЕПТ'}")
    print("-" * 85)

    step_num = 1
    for row in results:
        prod = str(row.stepResultLabel)
        ingreds = str(row.ingredients)
        recipe = str(row.recipeLabel)

        print(f"{step_num:<4} | {prod:<20} | {ingreds:<30} | {recipe}")
        step_num += 1


def interactive_session(g: Graph):
    print("\n=== ALCHEMY SPARQL CONSOLE ===")

    while True:
        print("\nВыберите действие:")
        print("1. [Использование] Где используется элемент X?")
        print("2. [Базовый крафт] Можно ли создать X из базовых?")
        print("3. [Прогноз] Что получится из X через N шагов?")
        print("4. [Полный крафт] Список всех рецептов для создания X")
        print("q. Выход")

        choice = input("\n>>> ").strip().lower()

        if choice in ('q', 'exit', 'quit', 'выход'):
            break

        if choice == '1':
            elem = input("Введите элемент: ").strip()
            query_uses_element(g, elem)

        elif choice == '2':
            elem = input("Введите элемент: ").strip()
            query_check_basic_craft(g, elem)

        elif choice == '3':
            elem = input("Введите начальный элемент: ").strip()
            steps = input("Количество шагов: ").strip()
            if steps.isdigit() and int(steps) > 0:
                query_reachable_iterative(g, elem, int(steps))
            else:
                print("Введите положительное число.")

        elif choice == '4':
            elem = input("Что хотите создать?: ").strip()
            query_crafting_tree(g, elem)

        else:
            print("Неверная команда.")


def main():
    g = load_graph(ONTO_FILE)
    interactive_session(g)


if __name__ == "__main__":
    main()
