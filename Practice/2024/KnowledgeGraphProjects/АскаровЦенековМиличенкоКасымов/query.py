# Импортируем необходимые библиотеки
from rdflib import Graph
import sys


def main(rdf_file):
    # Создаем граф и загружаем RDF файл
    g = Graph()
    try:
        g.parse(rdf_file, format=guess_format(rdf_file))
        print(f"RDF файл '{rdf_file}' успешно загружен.\n")
    except Exception as e:
        print(f"Ошибка при загрузке RDF файла: {e}")
        sys.exit(1)

    # 1. Какие рецепты предпочтиельнее выбрать человеку, страдающему недостатком витаминов группы B?
    query1 = """
    PREFIX ex: <http://example.org/>

    SELECT ?recipe (GROUP_CONCAT(?vitamin; separator=", ") AS ?vitamins)
    WHERE {
      ?recipe a ex:Product ;
              ex:hasIngredient ?ingredient ;
              ex:typeOfProduct ex:Recipe .

      ?ingredient ex:containsVitamin ?vitamin .
      FILTER(?vitamin IN (ex:витамин_в1, ex:витамин_в2, ex:витамин_в6, ex:витамин_в12))
    }
    GROUP BY ?recipe
    ORDER BY ?recipeName
    """

    print("1. Какие рецепты предпочтительнее выбрать человеку, страдающему недостатком витаминов группы B:")
    for row in g.query(query1):
        print(f"Рецепт: {row.recipe}, Витамины: {row.vitamins}")
    print("\n" + "=" * 80 + "\n")

    # 2. Какие ингредиенты используются чаще всего?
    query2 = """
        PREFIX ex: <http://example.org/> 
         
        SELECT ?ingredient (COUNT(?recipe) AS ?usageCount) 
        WHERE { 
          ?recipe a ex:Product ; 
                  ex:hasIngredient ?ingredient . 
        } 
        GROUP BY ?ingredient 
        ORDER BY DESC(?usageCount) 
        LIMIT 10
    """

    print("2. Какие ингредиенты используются чаще всего?")
    for row in g.query(query2):
        print(f"Рецепт URI: {row.ingredient}, Название: {row.usageCount}")
    print("\n" + "=" * 80 + "\n")

    # 3. Какие блюда и ингредиенты человеку лучше избегать с индивидуальной непереносимостью молока?
    query3 = """
    PREFIX ex: <http://example.org/>

    SELECT DISTINCT ?recipe
    WHERE {
      ?recipe a ex:Product ;
              ex:typeOfProduct ex:Recipe ;
              ex:hasIngredient ex:молоко .
    }
    ORDER BY ?recipe
    """

    print("3. Какие блюда и ингредиенты человеку лучше избегать с индивидуальной непереносимостью молока:")
    for row in g.query(query3):
        print(f"Количество рецептов: {row.recipe}")
    print("\n" + "=" * 80 + "\n")

    # 4. Какие рецепты можно приготовить, если доступны только два конкретных ингредиента, например, "сахар, банан, мука"?
    query4 = """
    PREFIX ex: <http://example.org/>

    SELECT ?recipe ?recipeName
    WHERE {
      ?recipe a ex:Product ;
              ex:hasIngredient ?ingredient ;
              ex:typeOfProduct ?recipeName.

      FILTER(?ingredient IN (ex:сахар, ex:банан, ex:мука))

      # Убедимся, что все ингредиенты рецепта входят в указанный список
      FILTER NOT EXISTS {
        ?recipe ex:hasIngredient ?otherIngredient .
        FILTER(?otherIngredient NOT IN (ex:сахар, ex:банан, ex:мука))
      }
    }
    GROUP BY ?recipe ?recipeName
    ORDER BY ?recipeName
    """

    print("4. Рецепты, которые можно приготовить только из ингредиентов 'сахар, банан, мука':")
    for row in g.query(query4):
        print(f"Рецепт URI: {row.recipe}, Название: {row.recipeName}")
    print("\n" + "=" * 80 + "\n")

    # 5. Какие рецепты содержат уникальные ингредиенты, которые не используются в других рецептах?
    query5 = """
    PREFIX ex: <http://example.org/>

    SELECT ?recipe ?recipeName ?uniqueIngredient
    WHERE {
      ?recipe a ex:Product ;
              ex:hasIngredient ?uniqueIngredient ;
              ex:typeOfProduct ?recipeName .

      # Проверяем, что этот ингредиент уникален
      FILTER NOT EXISTS {
        ?otherRecipe a ex:Product ;
                     ex:hasIngredient ?uniqueIngredient .
        FILTER(?otherRecipe != ?recipe)
      }
    }
    ORDER BY ?recipeName
    LIMIT 10
    """

    print("5. Рецепты с уникальными ингредиентами, не используемыми в других рецептах:")
    for row in g.query(query5):
        print(f"Рецепт URI: {row.recipe}, Название: {row.recipeName}, Уникальный ингредиент: {row.uniqueIngredient}")
    print("\n" + "=" * 80 + "\n")


def guess_format(filename):
    """Простая функция для определения формата RDF по расширению файла."""
    if filename.endswith('.ttl'):
        return 'turtle'
    elif filename.endswith('.rdf') or filename.endswith('.xml'):
        return 'xml'
    elif filename.endswith('.nt'):
        return 'nt'
    elif filename.endswith('.jsonld'):
        return 'json-ld'
    else:
        # По умолчанию пробуем 'xml'
        return 'xml'


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Использование: python script.py <путь_к_RDF_файлу>")
        sys.exit(1)

    rdf_file = sys.argv[1]
    main(rdf_file)
