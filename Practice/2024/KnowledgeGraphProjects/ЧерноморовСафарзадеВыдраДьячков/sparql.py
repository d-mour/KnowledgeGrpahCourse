import rdflib


def get_top_scorer_query(cost):
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX football: <http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#>
    
    SELECT ?player ?minutes_per_goal ?cost
    WHERE {
        ?cost_prop football:Принадлежит_игроку ?player .
        ?cost_prop rdf:type football:Цена .
        
        ?minutes_per_goal_prop football:Принадлежит_игроку ?player .
        ?minutes_per_goal_prop rdf:type football:Минут_для_гола .
        
        BIND(REPLACE(SUBSTR(STR(?minutes_per_goal_prop), 72), "_minutes_per_goal", "") AS ?minutes_per_goal_str)
        BIND(xsd:integer(?minutes_per_goal_str) AS ?minutes_per_goal)
        
        BIND(REPLACE(SUBSTR(STR(?cost_prop), 73), "_coast", "") AS ?cost_str)
        BIND(
            IF (
                STRENDS(STR(?cost_str), "m"), 
                xsd:double(SUBSTR(?cost_str, 1, STRLEN(?cost_str) - 1)) * 1000000,
                xsd:double(SUBSTR(?cost_str, 1, STRLEN(?cost_str) - 1)) * 1000
            ) AS ?cost
        )
        FILTER(BOUND(?minutes_per_goal))
        FILTER(?cost < """ + str(cost) + """)
    }
    ORDER BY ASC(?minutes_per_goal)
    LIMIT 10
    """

def get_top_goalkeeper_query(cost):
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX football: <http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#>

    SELECT ?player ?clean_sheets ?cost
    WHERE {
        ?cost_prop football:Принадлежит_игроку ?player .
        ?cost_prop rdf:type football:Цена .

        ?clean_sheets_prop football:Принадлежит_игроку ?player .
        ?clean_sheets_prop rdf:type football:Сухие_матчи .

        BIND(REPLACE(SUBSTR(STR(?clean_sheets_prop), 72), "_clean_sheets", "") AS ?clean_sheets_str)
        BIND(xsd:integer(?clean_sheets_str) AS ?clean_sheets)

        BIND(REPLACE(SUBSTR(STR(?cost_prop), 73), "_coast", "") AS ?cost_str)
        BIND(
            IF (
                STRENDS(STR(?cost_str), "m"), 
                xsd:double(SUBSTR(?cost_str, 1, STRLEN(?cost_str) - 1)) * 1000000,
                xsd:double(SUBSTR(?cost_str, 1, STRLEN(?cost_str) - 1)) * 1000
            ) AS ?cost
        )
        FILTER(BOUND(?clean_sheets))
        FILTER(?cost < """ + str(cost) + """)
    }
    ORDER BY DESC(?clean_sheets)
    LIMIT 10
    """

def get_top_assistant_query(cost):
    return """
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX football: <http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#>

    SELECT ?player ?assists ?cost
    WHERE {
        ?cost_prop football:Принадлежит_игроку ?player .
        ?cost_prop rdf:type football:Цена .

        ?assists_prop football:Принадлежит_игроку ?player .
        ?assists_prop rdf:type football:Голевые_передачи .

        BIND(REPLACE(SUBSTR(STR(?assists_prop), 72), "_assists", "") AS ?assists_str)
        BIND(xsd:integer(?assists_str) AS ?assists)

        BIND(REPLACE(SUBSTR(STR(?cost_prop), 73), "_coast", "") AS ?cost_str)
        BIND(
            IF (
                STRENDS(STR(?cost_str), "m"), 
                xsd:double(SUBSTR(?cost_str, 1, STRLEN(?cost_str) - 1)) * 1000000,
                xsd:double(SUBSTR(?cost_str, 1, STRLEN(?cost_str) - 1)) * 1000
            ) AS ?cost
        )
        FILTER(BOUND(?assists))
        FILTER(?cost < """ + str(cost) + """)
    }
    ORDER BY DESC(?assists)
    LIMIT 10
    """



graph = rdflib.Graph()
graph.parse("output.rdf", format="xml")
money = int(input("Введите стоимость в евро: "))

print("Топ 10 самых эффективных нападающих: ")
results = graph.query(get_top_scorer_query(money))
for row in results:
    print(f"Player : {row.player}, mpg: {row.minutes_per_goal}, cost: {row.cost}")

print("Топ 10 вратарей: ")
results = graph.query(get_top_goalkeeper_query(money))
for row in results:
    print(f"Player : {row.player}, clean_sheets: {row.clean_sheets}, cost: {row.cost}")

print("Топ 10 полузащитников: ")
results = graph.query(get_top_assistant_query(money))
for row in results:
    print(f"Player : {row.player}, assists: {row.assists}, cost: {row.cost}")