from rdflib import Graph

def main():
    rdf_file = "ontology.rdf"

    g = Graph()
    try:
        g.parse(rdf_file, format='xml')
        print(f"RDF файл '{rdf_file}' успешно загружен.\n")
    except Exception as e:
        print(f"Ошибка при загрузке RDF файла: {e}")
        return

    # 1. В какую геологическую эпоху жил этоникс?
    query1 = """
    PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

    SELECT ?epoch
    WHERE {
      :Этоникс :Жил_в_эпоху ?epoch .
    }
    """

    print("1. В какую геологическую эпоху жил этоникс:")
    for row in g.query(query1):
        print(f"Эпоха: {row.epoch}")
    print()

    # 2. К какому отряду принадлежит фукуизавр?
    query2 = """
    PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

    SELECT ?order
    WHERE {
      :Фукуизавр :принадлежит_отряду ?order .
    }
    """

    print("2. К какому отряду принадлежит фукуизавр:")
    for row in g.query(query2):
        print(f"Отряд: {row.order}")
    print()

    # 3. Какие века относятся к геологической эпохе верхний мел?
    query3 = """
    PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

    SELECT ?century
    WHERE {
      ?century :относится_к_эпохе :Верхний_мел .
    }
    """

    print("3. Какие века относятся к геологической эпохе верхний мел:")
    for row in g.query(query3):
        print(f"Век: {row.century}")
    print()

    # 4. Кто описал авимим и в каком году?
    query4 = """
    PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

    SELECT ?person ?year
    WHERE {
      :Авимим :described_by_whom ?person ;
               :year_of_description ?year .
    }
    """

    print("4. Кто описал авимим и в каком году:")
    for row in g.query(query4):
        print(f"Человек: {row.person}, Год: {row.year}")
    print()

    # 5. Какому отряду принадлежит семейство гадрозавриды?
    query5 = """
    PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

    SELECT ?order
    WHERE {
      :Гадрозавриды :принадлежит_отряду ?order .
    }
    """

    print("5. Какому отряду принадлежит семейство гадрозавриды:")
    for row in g.query(query5):
        print(f"Отряд: {row.order}")
    print()

    # 6. Какой динозавр был обнаружен позже всего?
    query_latest_discovery = """
        PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

        SELECT ?dinosaur ?year
        WHERE {
          ?dinosaur :year_of_discovery ?year .
        }
        ORDER BY DESC(?year)
        LIMIT 1
        """

    print("6. Самый поздний обнаруженный динозавр:")
    for row in g.query(query_latest_discovery):
        print(f"Динозавр: {row.dinosaur}, Год обнаружения: {row.year}")
    print()

    # 7. Все динозавры, описанные палеонтологом Алан_Х._Тернер.
    query_filter = """
        PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

        SELECT ?dinosaur
        WHERE {
          ?dinosaur :described_by_whom ?author .
          FILTER (?author = :Алан_Х._Тернер)
        }
        """

    print("7. Динозавры, описанные Алан_Х._Тернер:")
    for row in g.query(query_filter):
        print(f"Динозавр: {row.dinosaur}")
    print()

    # 8. Отряды динозавров, существовавшие в позднем меловом периоде.
    query_mesozoic_orders = """
        PREFIX : <http://www.semanticweb.org/алиночка/ontologies/2025/0/dinosaurus#>

        SELECT DISTINCT ?order
        WHERE {
          ?dinosaur :принадлежит_отряду ?order .
          ?dinosaur :Жил_в_эпоху :Верхний_мел .
        }
    """

    print("8. Отряды динозавров, существовавшие в позднем меловом периоде:")
    for row in g.query(query_mesozoic_orders):
        print(f"Отряд: {row.order}")
    print()


if __name__ == "__main__":
    main()
