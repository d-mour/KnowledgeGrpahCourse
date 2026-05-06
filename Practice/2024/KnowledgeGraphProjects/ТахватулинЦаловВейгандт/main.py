import json
from rdflib.namespace import OWL, RDF, RDFS
from rdflib import Graph, Namespace, RDF, RDFS, Literal, OWL, XSD, URIRef


def load_data_and_generate_ontology(champs_file, iron, bronze, silver, gold, platinum, emerald, diamond, master, output_file):
    ex = Namespace("http://example.org/lol#")
    g = Graph()
    g.bind("ex", ex)
    g.bind("owl", OWL)

    # Определение классов онтологии
    classes = ["Champion", "Role", "Rank", "Versus"]
    for cls in classes:
        g.add((ex[cls], RDF.type, OWL.Class))

    # Object Properties
    properties = {
        "hasRole": ("Champion", "Role"),
        "hasRank": ("Versus", "Rank"),
        "chosenChamp": ("Versus", "Champion"),
        "vsChamp": ("Versus", "Champion")
    }
    for prop, (domain, range_) in properties.items():
        g.add((ex[prop], RDF.type, OWL.ObjectProperty))
        g.add((ex[prop], RDFS.domain, ex[domain]))
        g.add((ex[prop], RDFS.range, ex[range_]))

    # Data Property для значения пикрейта, винрейта и банрейта
    g.add((ex.pickrateValue, RDFS.domain, ex.Pickrate))
    g.add((ex.pickrateValue, RDFS.range, XSD.float))

    g.add((ex.winrateValue, RDFS.domain, ex.Winrate))
    g.add((ex.winrateValue, RDFS.range, XSD.float))

    g.add((ex.banrateValue, RDFS.domain, ex.Banrate))
    g.add((ex.banrateValue, RDFS.range, XSD.float))

    # Загрузка данных из файлов
    with open(champs_file, 'r', encoding='utf-8') as f:
        champs_data = json.load(f)
    
    rank_datasets = []

    with open(iron, 'r', encoding='utf-8') as f:
        irons_data = json.load(f)
        rank_datasets.append(irons_data)

    with open(bronze, 'r', encoding='utf-8') as f:
        bronzes_data = json.load(f)
        rank_datasets.append(bronzes_data)

    with open(silver, 'r', encoding='utf-8') as f:
        silvers_data = json.load(f)
        rank_datasets.append(silvers_data)

    with open(gold, 'r', encoding='utf-8') as f:
        golds_data = json.load(f)
        rank_datasets.append(golds_data)

    with open(platinum, 'r', encoding='utf-8') as f:
        platinums_data = json.load(f)
        rank_datasets.append(platinums_data)

    with open(emerald, 'r', encoding='utf-8') as f:
        emeralds_data = json.load(f)
        rank_datasets.append(emeralds_data)

    with open(diamond, 'r', encoding='utf-8') as f:
        diamonds_data = json.load(f)
        rank_datasets.append(diamonds_data)

    with open(master, 'r', encoding='utf-8') as f:
        masters_data = json.load(f)
        rank_datasets.append(masters_data)

    # Добавление данных в граф
    for i, champ_data in enumerate(champs_data, start=1):
        ranks = ["iron", "bronze", "silver", "gold", "platinum", "emerald", "diamond", "master"]
        for j in ranks:
            rank = URIRef(ex[j])
            g.add((rank, RDF.type, ex.Rank))

        print(i, champ_data)
        # print(champ_data['Champion'].replace(" ", ""))

        champ = ex[champ_data['Champion'].replace(" ", "").lower()]
        g.add((champ, RDF.type, ex.Champion))
        
        for role in champ_data['Role']:
            role = role.replace(" ", "")
            # print(role)
            role_uri = URIRef(ex[role])
            g.add((role_uri, RDF.type, ex.Role))
            g.add((champ, ex.hasRole, role_uri))
        
        g.add((champ, ex.pickrateValue, Literal(champ_data['PickRate'], datatype=XSD.float)))
        g.add((champ, ex.winrateValue, Literal(champ_data['WinRate'], datatype=XSD.float)))
        g.add((champ, ex.banrateValue, Literal(champ_data['BanRate'], datatype=XSD.float)))

        for rank_dataset in rank_datasets:
            addVersuses(ex, g, rank_dataset)


    # Сохранение графа в файл OWL
    g.serialize(output_file, format="xml")
    print(f"OWL-файл успешно создан: {output_file}")
    return g

def addVersuses(ex, g, rank_data):
    for i, matchup in enumerate(rank_data, start=1):
        champion1 = matchup['champion1'].replace(" ", "")
        vsChampion = matchup['VsChampion'].replace(" ", "")
        rankName = matchup['Rank'].replace(" ", "")
        chosenChamp = ex[champion1]
        vsChamp = ex[vsChampion]
        rank = ex[rankName]

        individName = URIRef(f"http://example.org/versus/{champion1.upper()}vs{vsChampion.upper()}_{rankName.upper()}")

        g.add((individName, RDF.type, ex.Versus))
        g.add((individName, ex.chosenChamp, chosenChamp))
        g.add((individName, ex.vsChamp, vsChamp))
        g.add((individName, ex.hasRank, rank))
        g.add((individName, ex.winrateValue, Literal(matchup['winrate'], datatype=XSD.float)))

# ontology_graph = load_data_and_generate_ontology("parser/champions.json", "parser/vs_iron.json", "parser/vs_bronze.json", "parser/vs_silver.json", "parser/vs_gold.json", "parser/vs_platinum.json", "parser/vs_emerald.json", "parser/vs_diamond.json", "parser/vs_master.json", "main_ontology.owl")

def execute_sparql_query(graph, query):
    results = graph.query(query)
    for row in results:
        print(row)

def load_graph_from_owl(file_path):
    g = Graph()
    g.parse(file_path, format='xml')
    print(f"Граф успешно загружен из файла: {file_path}")
    return g

ontology_graph = load_graph_from_owl("main_ontology.owl")


if ontology_graph:
    # 10 чемпионов
    query1 = """
    PREFIX ex: <http://example.org/lol#>

    SELECT ?champion
    WHERE {
        ?champion a ex:Champion .
    }
    LIMIT 10
    """

    # 10 чемпионов с их винрейтом, пикрейтом и банрейтом
    query2 = """
    PREFIX ex: <http://example.org/lol#>

    SELECT ?champion ?winrate ?pickrate ?banrate
    WHERE {
        ?champion a ex:Champion ;
                ex:winrateValue ?winrate ;
                ex:pickrateValue ?pickrate ;
                ex:banrateValue ?banrate .
    }
    ORDER BY DESC(?pickrate)
    LIMIT 10
    """

    # все чемпионы с винрейтом выше 50%
    query3 = """
    PREFIX ex: <http://example.org/lol#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?champion ?winrate
    WHERE {
        ?champion a ex:Champion ;
                ex:winrateValue ?winrate .
        FILTER(?winrate > 50)
        FILTER(isLiteral(?winrate) && datatype(?winrate) = xsd:float)
    }
    ORDER BY DESC(?winrate)
    """

    # получение роли чемпиона
    query4 = """
    PREFIX ex: <http://example.org/lol#>

    SELECT ?champion ?role
    WHERE {
        ?champion a ex:Champion ;
                ex:hasRole ?role .
        FILTER(?champion = ex:pyke)
    }
    """

    # винрейт одного чемпиона против другого на всех рейтингах
    query5 = """
    PREFIX ex: <http://example.org/lol#>
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

    SELECT ?versus ?chosenChamp ?vsChamp ?rank ?winrate
    WHERE {
        ?versus a ex:Versus ;
                ex:chosenChamp ?chosenChamp ;
                ex:vsChamp ?vsChamp ;
                ex:hasRank ?rank ;
                ex:winrateValue ?winrate .
        FILTER(?chosenChamp = ex:pyke)
        FILTER(?vsChamp = ex:braum)
    }
    ORDER BY DESC(?winrate)
    """

    print("Запрос 1:")
    execute_sparql_query(ontology_graph, query1)
    print("Запрос 2:")
    execute_sparql_query(ontology_graph, query2)
    print("Запрос 3:")
    execute_sparql_query(ontology_graph, query3)
    print("Запрос 4:")
    execute_sparql_query(ontology_graph, query4)
    print("Запрос 5:")
    execute_sparql_query(ontology_graph, query5)
