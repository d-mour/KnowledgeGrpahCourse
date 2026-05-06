import json
from rdflib.namespace import OWL, RDF, RDFS
from rdflib import Graph, Namespace, RDF, RDFS, Literal, OWL, XSD, URIRef
def load_data_and_generate_ontology(result_file, ranks_file, skills_file, lineups_file, winrate_with_file, output_file):
    ex = Namespace("http://example.org/valorant#")
    g = Graph()
    g.bind("ex", ex)
    g.bind("owl", OWL)

    # Определение классов онтологии
    classes = ["Agent", "Map", "Rank", "Winrate", "Skill", "Lineup"]
    for cls in classes:
        g.add((ex[cls], RDF.type, OWL.Class))

    # Object Properties
    properties = {
        "hasAgent": ("Winrate", "Agent"),
        "hasMap": ("Winrate", "Map"),
        "hasRank": ("Winrate", "Rank"),
        "hasSkill": ("Agent", "Skill"),
        "hasLineup": ("Map", "Skill"),
        "withAgent": ("Winrate", "Agent")
    }
    for prop, (domain, range_) in properties.items():
        g.add((ex[prop], RDF.type, OWL.ObjectProperty))
        g.add((ex[prop], RDFS.domain, ex[domain]))
        g.add((ex[prop], RDFS.range, ex[range_]))

    # Data Property для значения винрейта
    g.add((ex.winrateValue, RDF.type, OWL.DatatypeProperty))
    g.add((ex.winrateValue, RDFS.domain, ex.Winrate))
    g.add((ex.winrateValue, RDFS.range, XSD.float))

    # Загрузка данных из файлов
    with open(result_file, 'r', encoding='utf-8') as f:
        agents_data = json.load(f)
    
    with open(ranks_file, 'r', encoding='utf-8') as f:
        ranks_data = json.load(f)
    
    with open(skills_file, 'r', encoding='utf-8') as f:
        skills_data = json.load(f)

    with open(lineups_file, 'r', encoding='utf-8') as f:
        lineups_data = json.load(f)

    with open(winrate_with_file, 'r', encoding='utf-8') as f:
        agents_with_agent_data = json.load(f)

    # Обратное сопоставление рангов
    rank_lookup = {v: k for k, v in ranks_data.items()}

    # Добавление данных в граф
    for i, agent_data in enumerate(agents_data, start=1):
        agent = ex[agent_data['name'].capitalize()]
        g.add((agent, RDF.type, ex.Agent))
        
        map_uri = ex[agent_data['map'].capitalize()]
        g.add((map_uri, RDF.type, ex.Map))
        
        rank_name = rank_lookup.get(agent_data['rank'], "Unknown")
        rank_uri = ex[rank_name.replace(" ", "_")]
        g.add((rank_uri, RDF.type, ex.Rank))
        
        winrate_uri = ex[f"Winrate{i}"]
        g.add((winrate_uri, RDF.type, ex.Winrate))
        g.add((winrate_uri, ex.hasAgent, agent))
        g.add((winrate_uri, ex.hasMap, map_uri))
        g.add((winrate_uri, ex.hasRank, rank_uri))
        g.add((winrate_uri, ex.winrateValue, Literal(agent_data['winrate'], datatype=XSD.float)))

    for i, agent_data in enumerate(agents_with_agent_data, start=1):
        agent = ex[agent_data['name'].capitalize()]
        with_agent = ex[agent_data['withAgent'].capitalize()]  # Добавляем связь withAgent
        
        g.add((agent, RDF.type, ex.Agent))
        g.add((with_agent, RDF.type, ex.Agent))  # Убедимся, что withAgent тоже добавлен как Agent
        
        map_uri = ex[agent_data['map'].capitalize()]
        g.add((map_uri, RDF.type, ex.Map))
        
        rank_name = rank_lookup.get(agent_data['rank'], "Unknown")
        rank_uri = ex[rank_name.replace(" ", "_")]
        g.add((rank_uri, RDF.type, ex.Rank))
        
        winrate_uri = ex[f"Winrate{i}"]
        g.add((winrate_uri, RDF.type, ex.Winrate))
        g.add((winrate_uri, ex.hasAgent, agent))
        g.add((winrate_uri, ex.withAgent, with_agent))  # Добавляем связь withAgent
        g.add((winrate_uri, ex.hasMap, map_uri))
        g.add((winrate_uri, ex.hasRank, rank_uri))
        g.add((winrate_uri, ex.winrateValue, Literal(agent_data['winrate'], datatype=XSD.float)))


    # Добавление навыков
    for agent_skill in skills_data:
        agent_uri = ex[agent_skill['agent'].capitalize()]
        for skill_name in agent_skill['skills']:
            skill_uri = ex[skill_name.replace(" ", "_")]
            g.add((skill_uri, RDF.type, ex.Skill))
            g.add((agent_uri, ex.hasSkill, skill_uri))

    

    for lineup in lineups_data:
        map_uri = ex[lineup['map'].capitalize()]
        skill_uri = ex[lineup['skill'].replace(" ", "_")]
        g.add((map_uri, ex.hasLineup, skill_uri))

    # Сохранение графа в файл OWL
    g.serialize(output_file, format="xml")
    print(f"OWL-файл успешно создан: {output_file}")
    return g

# Использование функции


# Функция для выполнения SPARQL-запроса
def execute_sparql_query(graph, query):
    results = graph.query(query)
    for row in results:
        print(row)


# Использование функции
#ontology_graph = load_data_and_generate_ontology("result.json",  "data/ranks.json", "agents_skills.json", "lineups.json", "winrate_with_data.json", "valorant_ontology_with_skills.owl")

def load_graph_from_owl(file_path):
    g = Graph()
    g.parse(file_path, format='xml')  # Загружаем OWL-файл в формате XML
    print(f"Граф успешно загружен из файла: {file_path}")
    return g

# Пример использования функции
ontology_graph = load_graph_from_owl("valorant_ontology_with_skills.owl")

if ontology_graph:
    query = """
    PREFIX ex: <http://example.org/valorant#>

    SELECT ?agent (STR(?winrate) AS ?winrateValue)
    WHERE {
        ?winrateInstance ex:hasMap ex:Bind ;
                        ex:hasAgent ?agent ;
                        ex:hasRank ex:Iron_3 ;
                        ex:winrateValue ?winrate .
        
        # Проверка наличия лайнапа на карте Bind для навыков агента
        ?agent ex:hasSkill ?skill .
        ex:Bind ex:hasLineup ?skill .
        
        FILTER (?agent != ex:Phoenix)
        FILTER (?agent != ex:Raze)
        FILTER (?agent != ex:Killjoy)
    }
    ORDER BY DESC(?winrate)
    LIMIT 1
    """

    #Агент с лучшим винрейтом на карте Bind с другим агентом и наличием у первого 1 лайнапа
    query2 = """PREFIX ex: <http://example.org/valorant#>
        SELECT ?agent (STR(?winrate) AS ?winrateValue)
        WHERE {
            ?winrateInstance ex:hasMap ex:Split ;
                            ex:hasAgent ?agent ;
                            ex:withAgent ex:Cypher ;
                            ex:winrateValue ?winrate .
        }
        ORDER BY DESC(?winrate)
        LIMIT 1
    """
    #Агенты с наибольшим общим количеством лайнапов на всех картах
    query3 = """PREFIX ex: <http://example.org/valorant#>
    SELECT ?agent (COUNT(?skill) AS ?totalLineups)
    WHERE {
        ?agent ex:hasSkill ?skill .
        ?map ex:hasLineup ?skill .
    }
    GROUP BY ?agent
    ORDER BY DESC(?totalLineups)
    LIMIT 1
    """

    #Лучший агент на карте Haven, играя на ранге Diamond 2 с другим агентом

    query4 = """PREFIX ex: <http://example.org/valorant#>
    SELECT ?agent ?withAgent (STR(?winrate) AS ?winrateValue)
    WHERE {
        ?winrateInstance ex:hasMap ex:Haven ;
                        ex:hasAgent ?agent ;
                        ex:withAgent ?withAgent ;
                        ex:hasRank ex:Diamond_2 ;
                        ex:winrateValue ?winrate .
    }
    ORDER BY DESC(?winrate)
    LIMIT 1
    """

    #Агенты с самым высоким винрейтом на карте Split среди всех рангов, у которых есть хотя бы один лайнап
    query5 = """PREFIX ex: <http://example.org/valorant#>
    SELECT ?agent (AVG(?winrate) AS ?averageWinrate)
    WHERE {
        ?winrateInstance ex:hasMap ex:Split ;
                        ex:hasAgent ?agent ;
                        ex:winrateValue ?winrate .
        
        # Проверка на наличие хотя бы одного лайнапа на карте Split
        ?agent ex:hasSkill ?skill .
        ex:Split ex:hasLineup ?skill .
    }
    GROUP BY ?agent
    ORDER BY DESC(?averageWinrate)
    LIMIT 3
    """

    # Выполнение запроса
    print("Запрос 1:")
    execute_sparql_query(ontology_graph, query)
    print("Запрос 2:")
    execute_sparql_query(ontology_graph, query2)
    print("Запрос 3:")
    execute_sparql_query(ontology_graph, query3)
    print("Запрос 4:")
    execute_sparql_query(ontology_graph, query4)
    print("Запрос 5:")
    execute_sparql_query(ontology_graph, query5)
