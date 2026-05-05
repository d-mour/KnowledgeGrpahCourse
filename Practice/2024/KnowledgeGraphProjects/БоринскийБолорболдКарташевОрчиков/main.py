import requests
from rdflib import Graph, Literal, RDF, URIRef, Namespace
from rdflib.namespace import XSD, RDFS
import urllib.parse
import time
import datetime
import sys

API_KEY = '14c283758a95445691892bacf73a2ab9'
OWL_FILE_PATH = 'updated_ontology_20241118_221052.owl'

CATEGORIES = [
    "main course", "side dish", "dessert", "appetizer", "salad",
    "bread", "breakfast", "soup", "beverage", "sauce",
    "marinade", "fingerfood", "snack", "drink"
]

CUISINES = [
    "African", "Cajun", "Caribbean", "Eastern European", "Irish", "Jewish", "Middle Eastern",
    "Asian", "American", "British", "Chinese", "European", "French",
    "German", "Greek", "Indian", "Italian",
    "Japanese", "Korean", "Latin American", "Mediterranean",
    "Mexican", "Nordic", "Southern", "Spanish",
    "Thai", "Vietnamese"
]


def request_with_retry(url, params, max_retries=5):
    global API_KEY
    retries = 0
    while retries < max_retries:
        try:
            response = requests.get(url, params=params)
            status = response.status_code

            if status == 200:
                return response
            elif status == 402:
                print("Ошибка 402: Требуется новый API ключ.")
                API_KEY = input("Пожалуйста, введите новый API ключ: ").strip()
                params['apiKey'] = API_KEY
                retries += 1
            elif status == 429:
                retry_after = response.headers.get("Retry-After")
                wait_time = int(retry_after) if retry_after and retry_after.isdigit() else 60
                print(f"Ошибка 429: Слишком много запросов. Ждем {wait_time} секунд перед повторной попыткой.")
                time.sleep(wait_time)
                retries += 1
            elif 400 <= status < 500:
                print(f"Клиентская ошибка {status}. Пропускаем запрос.")
                return None
            elif 500 <= status < 600:
                print(f"Серверная ошибка {status}. Ждем 30 секунд перед повторной попыткой.")
                time.sleep(30)
                retries += 1
            else:
                print(f"Неизвестный статус код {status}. Пропускаем запрос.")
                return None
        except requests.exceptions.RequestException as e:
            print(f"Исключение при запросе: {e}. Ждем 30 секунд перед повторной попыткой.")
            time.sleep(30)
            retries += 1

    print("Превышено максимальное количество попыток. Пропускаем запрос.")
    return None


def get_recipes_by_cuisine(cuisine, number=3, offset=0):
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'cuisine': cuisine,
        'number': number,
        'apiKey': API_KEY,
        'offset': offset
    }
    response = request_with_retry(url, params)
    if response and response.status_code == 200:
        return response.json().get('results', [])
    else:
        print(f"Не удалось получить рецепты для кухни: {cuisine}")
        return []


def get_recipe_information(recipe_id):
    url = f'https://api.spoonacular.com/recipes/{recipe_id}/information'
    params = {
        'includeNutrition': 'true',
        'apiKey': API_KEY
    }
    response = request_with_retry(url, params)
    if response and response.status_code == 200:
        data = response.json()
        recipe_data = {
            'id': recipe_id,
            'name': data['title'],
            'ingredients': [ingredient['name'] for ingredient in data['extendedIngredients']],
            'time': data['readyInMinutes'],
            'type': data.get('dishTypes', []),
            'diet': data.get('diets', []),
            'calories': None,
            'fatContent': None,
            'carbohydrateContent': None,
            'proteinContent': None
        }
        if 'nutrition' in data and 'nutrients' in data['nutrition']:
            for nutrient in data['nutrition']['nutrients']:
                if nutrient['name'] == 'Calories':
                    recipe_data['calories'] = nutrient['amount']
                elif nutrient['name'] == 'Fat':
                    recipe_data['fatContent'] = nutrient['amount']
                elif nutrient['name'] == 'Carbohydrates':
                    recipe_data['carbohydrateContent'] = nutrient['amount']
                elif nutrient['name'] == 'Protein':
                    recipe_data['proteinContent'] = nutrient['amount']
        return recipe_data
    else:
        print(f"Не удалось получить информацию о рецепте с ID: {recipe_id}")
        return None


def safe_uri(name):
    """Создает безопасный URI из строки, заменяя пробелы на подчеркивания и кодируя специальные символы."""
    name_with_underscores = name.replace(" ", "_")
    return URIRef(BASE + urllib.parse.quote_plus(name_with_underscores.lower()))


def find_existing_resource_by_name(graph, rdf_type, label):
    """
    Ищет существующий ресурс по типу и метке.
    Возвращает URI ресурса, если найден, иначе None.
    """
    query = """
    SELECT ?s WHERE {
        ?s a <%s> ;
           <%s#name> "%s" .
    }
    """ % (rdf_type, BASE, label.replace('"', '\\"'))
    results = graph.query(query)
    for row in results:
        return row.s
    return None


def is_recipe_present(graph, recipe_name):
    """
    Проверяет, существует ли рецепт с данным именем в онтологии.
    Возвращает True, если рецепт существует, иначе False.
    """
    recipe_uri = safe_uri(f"recipe_{recipe_name}")
    return (recipe_uri, RDF.type, RECIPE_CLASS) in graph


def add_category(graph, category_name):
    existing = find_existing_resource_by_name(graph, CATEGORY_CLASS, category_name)
    if existing:
        return existing
    category_uri = safe_uri(f"category_{category_name}")
    graph.add((category_uri, RDF.type, CATEGORY_CLASS))
    graph.add((category_uri, RDFS.label, Literal(category_name)))
    graph.add((category_uri, NAME, Literal(category_name)))
    return category_uri


def add_cuisine(graph, cuisine_name):
    existing = find_existing_resource_by_name(graph, CUISINE_CLASS, cuisine_name)
    if existing:
        return existing
    cuisine_uri = safe_uri(f"cuisine_{cuisine_name}")
    graph.add((cuisine_uri, RDF.type, CUISINE_CLASS))
    graph.add((cuisine_uri, RDFS.label, Literal(cuisine_name)))
    graph.add((cuisine_uri, NAME, Literal(cuisine_name)))
    return cuisine_uri


def add_dietary_restriction(graph, diet_name):
    existing = find_existing_resource_by_name(graph, DIETARY_RESTRICTION_CLASS, diet_name)
    if existing:
        return existing
    diet_uri = safe_uri(f"diet_{diet_name}")
    graph.add((diet_uri, RDF.type, DIETARY_RESTRICTION_CLASS))
    graph.add((diet_uri, RDFS.label, Literal(diet_name)))
    graph.add((diet_uri, NAME, Literal(diet_name)))
    return diet_uri


def add_ingredient(graph, ingredient_name):
    existing = find_existing_resource_by_name(graph, INGREDIENT_CLASS, ingredient_name)
    if existing:
        return existing
    ingredient_uri = safe_uri(f"ingredient_{ingredient_name}")
    graph.add((ingredient_uri, RDF.type, INGREDIENT_CLASS))
    graph.add((ingredient_uri, RDFS.label, Literal(ingredient_name)))
    graph.add((ingredient_uri, NAME, Literal(ingredient_name)))
    return ingredient_uri


def add_recipe(graph, recipe_data, cuisine_uri):
    recipe_uri = safe_uri(f"recipe_{recipe_data['name']}")

    if (recipe_uri, RDF.type, RECIPE_CLASS) in graph:
        print(f"Рецепт '{recipe_data['name']}' уже существует. Пропускаем добавление.")
        return recipe_uri

    graph.add((recipe_uri, RDF.type, RECIPE_CLASS))
    graph.add((recipe_uri, NAME, Literal(recipe_data['name'])))

    graph.add((recipe_uri, URIRef(BASE + "recipeID"), Literal(recipe_data['id'], datatype=XSD.integer)))

    if recipe_data['calories'] is not None:
        graph.add((recipe_uri, CALORIES, Literal(recipe_data['calories'], datatype=XSD.double)))
    if recipe_data['fatContent'] is not None:
        graph.add((recipe_uri, FAT_CONTENT, Literal(recipe_data['fatContent'], datatype=XSD.double)))
    if recipe_data['carbohydrateContent'] is not None:
        graph.add((recipe_uri, CARBOHYDRATE_CONTENT, Literal(recipe_data['carbohydrateContent'], datatype=XSD.double)))
    if recipe_data['proteinContent'] is not None:
        graph.add((recipe_uri, PROTEIN_CONTENT, Literal(recipe_data['proteinContent'], datatype=XSD.double)))
    if recipe_data['time'] is not None:
        graph.add((recipe_uri, TIME, Literal(recipe_data['time'], datatype=XSD.nonNegativeInteger)))

    for category in recipe_data['type']:
        if category in CATEGORIES:
            category_uri = add_category(graph, category)
            graph.add((recipe_uri, HAS_CATEGORY, category_uri))

    graph.add((recipe_uri, BELONGS_TO_CUISINE, cuisine_uri))

    for diet in recipe_data['diet']:
        diet_uri = add_dietary_restriction(graph, diet)
        graph.add((recipe_uri, HAS_DIETARY_RESTRICTION, diet_uri))

    for ingredient in recipe_data['ingredients']:
        ingredient_uri = add_ingredient(graph, ingredient)
        graph.add((recipe_uri, USES, ingredient_uri))

    return recipe_uri


def main():
    global graph, BASE, CATEGORY_CLASS, CUISINE_CLASS, DIETARY_RESTRICTION_CLASS, INGREDIENT_CLASS, RECIPE_CLASS
    global NAME, CALORIES, FAT_CONTENT, CARBOHYDRATE_CONTENT, PROTEIN_CONTENT, TIME
    global HAS_CATEGORY, BELONGS_TO_CUISINE, HAS_DIETARY_RESTRICTION, USES

    BASE = "http://www.semanticweb.org/admin/ontologies/2024/9/untitled-ontology-10#"
    ONS = Namespace(BASE)

    graph = Graph()
    try:
        graph.parse(OWL_FILE_PATH, format='application/rdf+xml')
        print(f"Онтология успешно загружена из {OWL_FILE_PATH}.")
    except Exception as e:
        print(f"Не удалось загрузить онтологию из {OWL_FILE_PATH}: {e}")
        sys.exit(1)

    CATEGORY_CLASS = ONS.Category
    CUISINE_CLASS = ONS.Cuisine
    DIETARY_RESTRICTION_CLASS = ONS.DietaryRestriction
    INGREDIENT_CLASS = ONS.Ingredient
    RECIPE_CLASS = ONS.Recipe

    NAME = ONS.name
    CALORIES = ONS.calories
    FAT_CONTENT = ONS.fatContent
    CARBOHYDRATE_CONTENT = ONS.carbohydrateContent
    PROTEIN_CONTENT = ONS.proteinContent
    TIME = ONS.time

    HAS_CATEGORY = ONS.hasCategory
    BELONGS_TO_CUISINE = ONS.belongsToCuisine
    HAS_DIETARY_RESTRICTION = ONS.hasDietaryRestriction
    USES = ONS.uses

    for category in CATEGORIES:
        add_category(graph, category)

    cuisine_uris = {}
    for cuisine in CUISINES:
        cuisine_uri = add_cuisine(graph, cuisine)
        cuisine_uris[cuisine] = cuisine_uri

    try:
        for cuisine in CUISINES:
            print(f"Обрабатываем кухню: {cuisine}")
            recipes = get_recipes_by_cuisine(cuisine, number=100)
            cuisine_uri = cuisine_uris[cuisine]

            for recipe in recipes:
                recipe_name = recipe["title"]

                if is_recipe_present(graph, recipe_name):
                    print(f"Рецепт '{recipe_name}' уже существует в онтологии. Пропускаем.")
                    continue

                recipe_id = recipe["id"]

                recipe_info = get_recipe_information(recipe_id)
                if recipe_info:
                    add_recipe(graph, recipe_info, cuisine_uri)
                    print(f"Добавлен рецепт: {recipe_info['name']}")
                else:
                    print(f"Не удалось получить информацию о рецепте с ID: {recipe_id}")
    except KeyboardInterrupt:
        print("Прерывание пользователем. Сохраняем текущие данные.")
    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:

        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        OUTPUT_OWL_FILE = f"updated_ontology.owl"

        try:
            graph.serialize(destination=OUTPUT_OWL_FILE, format='application/rdf+xml')
            print(f"Онтология успешно сохранена в {OUTPUT_OWL_FILE}")
        except Exception as e:
            print(f"Не удалось сохранить онтологию: {e}")


if __name__ == "__main__":
    main()
