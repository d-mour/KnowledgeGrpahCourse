from rdflib import Graph, Namespace, URIRef, Literal, RDF, OWL, RDFS
import json

# Создание пустого графа
g = Graph()

# Парсинг RDF файла
g.parse("laba-grafs.rdf", format="xml")

# Определение пространства имен
n = Namespace("http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#")

gson = json.loads(open("output.json", "r", encoding="UTF-8").read())
for club in gson:
    name_club = "_".join(club['club_name'].split())
    club_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{name_club}_club")
    g.add((club_uri, RDF.type, n.Клуб))

    for player in club['players']:
        name = "_".join(player['name'].split())
        name_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{name}_player")
        g.add((name_uri, RDF.type, n.Игрок))
        g.add((name_uri, n.Принадлежит_клубу, club_uri))

        position = "_".join(player['position'].split())
        add_position = n[position]
        g.add((add_position, RDFS.subClassOf, n.Амплуа))

        position_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{position}_position")
        g.add((position_uri, RDF.type, add_position))
        g.add((position_uri, n.Принадлежит_игроку, name_uri))

        cost = player['cost']
        cost_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{cost}_coast")
        g.add((cost_uri, RDF.type, n.Цена))
        g.add((cost_uri, n.Принадлежит_игроку, name_uri))

        stat = player['detailed_stats']

        goals = stat['Goals']
        goals_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{goals}_goals")
        g.add((goals_uri, RDF.type, n.Голы))
        g.add((goals_uri, n.Принадлежит_игроку, name_uri))

        if ("Assists" in stat):
            assists = stat['Assists']
            assists_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{assists}_assists")
            g.add((assists_uri, RDF.type, n.Голевые_передачи))
            g.add((assists_uri, n.Принадлежит_игроку, name_uri))

        appearances = stat['Appearances']
        appearances_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{appearances}_appearances")
        g.add((appearances_uri, RDF.type, n.Появления_на_поле))
        g.add((appearances_uri, n.Принадлежит_игроку, name_uri))

        own_goals = stat['Own goals']
        own_goals_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{own_goals}_own_goals")
        g.add((own_goals_uri, RDF.type, n.Автоголы))
        g.add((own_goals_uri, n.Принадлежит_игроку, name_uri))

        substitutions_on = stat['Substitutions on']
        substitutions_on_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{substitutions_on}_substitutions_on")
        g.add((substitutions_on_uri, RDF.type, n.Замена_выход))
        g.add((substitutions_on_uri, n.Принадлежит_игроку, name_uri))

        substitutions_off = stat['Substitutions off']
        substitutions_off_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{substitutions_off}_substitutions_off")
        g.add((substitutions_off_uri, RDF.type, n.Замена_уход))
        g.add((substitutions_off_uri, n.Принадлежит_игроку, name_uri))

        yellow_cards = stat['Yellow cards']
        yellow_cards_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{yellow_cards}_yellow_cards")
        g.add((yellow_cards_uri, RDF.type, n.Желтые_карточки))
        g.add((yellow_cards_uri, n.Принадлежит_игроку, name_uri))

        second_yellow_cards = stat['Second yellow cards']
        second_yellow_cards_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{second_yellow_cards}_second_yellow_cards")
        g.add((second_yellow_cards_uri, RDF.type, n.Вторые_желтые_карточки))
        g.add((second_yellow_cards_uri, n.Принадлежит_игроку, name_uri))

        red_cards = stat['Red cards']
        red_cards_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{red_cards}_red_cards")
        g.add((red_cards_uri, RDF.type, n.Красные_карточки))
        g.add((red_cards_uri, n.Принадлежит_игроку, name_uri))

        if ("Goals conceded" in stat):
            goals_conceded = stat['Goals conceded']
            goals_conceded_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{goals_conceded}_goals_conceded")
            g.add((goals_conceded_uri, RDF.type, n.Пропущенные_голы))
            g.add((goals_conceded_uri, n.Принадлежит_игроку, name_uri))

        if ("Clean sheets" in stat):
            clean_sheets = stat['Clean sheets']
            clean_sheets_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{clean_sheets}_clean_sheets")
            g.add((clean_sheets_uri, RDF.type, n.Сухие_матчи))
            g.add((clean_sheets_uri, n.Принадлежит_игроку, name_uri))

        minutes_played = stat['Minutes played'].replace("'", "").replace(".", "")
        minutes_played_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{minutes_played}_minutes_played")
        g.add((minutes_played_uri, RDF.type, n.Время_на_поле))
        g.add((minutes_played_uri, n.Принадлежит_игроку, name_uri))

        if ("Penalty goals" in stat):
            penalty_goals = stat['Penalty goals']
            penalty_goals_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{penalty_goals}_penalty_goals")
            g.add((penalty_goals_uri, RDF.type, n.Голы_пенальти))
            g.add((penalty_goals_uri, n.Принадлежит_игроку, name_uri))

        if ("Minutes per goal" in stat):
            minutes_per_goal = stat['Minutes per goal'].replace("'", "").replace(".", "")
            minutes_per_goal_uri = URIRef(f"http://www.semanticweb.org/msi/ontologies/2024/10/untitled-ontology-12#{minutes_per_goal}_minutes_per_goal")
            g.add((minutes_per_goal_uri, RDF.type, n.Минут_для_гола))
            g.add((minutes_per_goal_uri, n.Принадлежит_игроку, name_uri))
       

g.serialize(destination='output.rdf', format='xml')