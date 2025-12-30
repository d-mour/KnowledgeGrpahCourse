from rdflib import Graph, Namespace, RDF, RDFS, FOAF, Literal
import pandas as pd

g = Graph()
g.parse("cs2_ontology_raw.rdf")

CS2 = Namespace("http://cs2-ontology#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
g.bind("cs2", CS2)
g.bind("foaf", FOAF)


def run_query(query, title):
    try:
        results = g.query(query)
        data = []

        for row in results:
            row_dict = {}
            for i, var in enumerate(results.vars):
                value = row[i]
                if value:
                    val_str = str(value)
                    if '#' in val_str:
                        val_str = val_str.split('#')[-1]
                    if 'http://' in val_str:
                        val_str = val_str.split('/')[-1]
                    if 'country_' in val_str:
                        val_str = val_str.replace('country_', '')
                    if 'team_' in val_str:
                        val_str = val_str.replace('team_', '')
                    row_dict[str(var)] = val_str
                else:
                    row_dict[str(var)] = "-"
            data.append(row_dict)
        if data:
            df = pd.DataFrame(data)

            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', None)
            print(df.to_string(index=False))

            pd.reset_option('display.max_rows')
            pd.reset_option('display.max_columns')
            pd.reset_option('display.width')
        print(f"\n{'=' * 70}")



    except Exception as e:
        print(f"{e}")


# топ игроков по рейтингу
query1 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?rating ?kills_per_death ?headshot_percentage ?damage_per_round WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:rating ?rating .
    ?player cs2:kills_per_death ?kills_per_death .
    ?player cs2:headshot_percentage ?headshot_percentage .
    ?player cs2:damage_per_round ?damage_per_round .
    FILTER(?rating > 1.1)
}
ORDER BY DESC(?rating)
"""
run_query(query1, "")

# страны с лучшими игроками
query2 = """
PREFIX cs2: <http://cs2-ontology#>

SELECT ?country (COUNT(?player) as ?playerCount) 
       (AVG(?rating) as ?avgRating) 
       (AVG(?kills_per_death) as ?avgKDR) 
       (AVG(?headshot_percentage) as ?avgHS) WHERE {
    ?player a cs2:Player .
    ?player cs2:fromCountry ?country .
    ?player cs2:rating ?rating .
    ?player cs2:kills_per_death ?kills_per_death .
    ?player cs2:headshot_percentage ?headshot_percentage .
}
GROUP BY ?country
HAVING (COUNT(?player) >= 3)
ORDER BY DESC(?avgRating)
"""
run_query(query2, "")

# лучшие снайперы
query3 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?headshot_percentage ?sniper_kills ?rating ?kills_per_death WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:headshot_percentage ?headshot_percentage .
    ?player cs2:sniper_kills ?sniper_kills .
    ?player cs2:rating ?rating .
    ?player cs2:kills_per_death ?kills_per_death .
    FILTER(?headshot_percentage > 50 && ?sniper_kills > 100)
}
ORDER BY DESC(?headshot_percentage)
"""
run_query(query3, "")

# игроки с высоким opening kill ratio
query4 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?opening_kill_ratio ?rating ?damage_per_round ?total_opening_kills WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:opening_kill_ratio ?opening_kill_ratio .
    ?player cs2:rating ?rating .
    ?player cs2:damage_per_round ?damage_per_round .
    ?player cs2:total_opening_kills ?total_opening_kills .
    FILTER(?opening_kill_ratio > 1.2)
}
ORDER BY DESC(?opening_kill_ratio)
"""
run_query(query4, "")

# командные игроки
query5 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?assists_per_round ?rating ?saved_teammates_per_round WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:assists_per_round ?assists_per_round .
    ?player cs2:rating ?rating .
    ?player cs2:saved_teammates_per_round ?saved_teammates_per_round .
    FILTER(?assists_per_round > 0.15)
}
ORDER BY DESC(?assists_per_round)
"""
run_query(query5, "")

# молодые таланты
query6 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?age ?rating ?headshot_percentage ?kills_per_death WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:age ?age .
    ?player cs2:rating ?rating .
    ?player cs2:headshot_percentage ?headshot_percentage .
    ?player cs2:kills_per_death ?kills_per_death .
    FILTER(?age < 22 && ?rating > 1.05)
}
ORDER BY DESC(?rating)
"""
run_query(query6, "")

# специалисты по винтовкам
query7 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?rifle_kills ?total_kills ?rating ?headshot_percentage WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:rifle_kills ?rifle_kills .
    ?player cs2:total_kills ?total_kills .
    ?player cs2:rating ?rating .
    ?player cs2:headshot_percentage ?headshot_percentage .
    FILTER(?total_kills > 500 && (?rifle_kills / ?total_kills) > 0.5)
}
ORDER BY DESC(?rifle_kills)
"""
run_query(query7, "")

# опытные игроки
query8 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?maps_played ?rating ?age ?kills_per_death WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:maps_played ?maps_played .
    ?player cs2:rating ?rating .
    ?player cs2:age ?age .
    ?player cs2:kills_per_death ?kills_per_death .
    FILTER(?maps_played > 200 && ?rating > 1.0)
}
ORDER BY DESC(?maps_played)
"""
run_query(query8, "")

# cтатистика команд
query9 = """
PREFIX cs2: <http://cs2-ontology#>

SELECT ?team (COUNT(?player) as ?playerCount) 
       (AVG(?rating) as ?avgRating) 
       (AVG(?kills_per_death) as ?avgKDR) 
       (AVG(?headshot_percentage) as ?avgHS) WHERE {
    ?player a cs2:Player .
    ?player cs2:playsFor ?team .
    ?player cs2:rating ?rating .
    ?player cs2:kills_per_death ?kills_per_death .
    ?player cs2:headshot_percentage ?headshot_percentage .
}
GROUP BY ?team
HAVING (COUNT(?player) >= 2)
ORDER BY DESC(?avgRating)
"""
run_query(query9, "")

# c,алансированные игроки
query10 = """
PREFIX cs2: <http://cs2-ontology#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?player ?nick ?rating ?kills_per_death ?headshot_percentage ?damage_per_round ?assists_per_round WHERE {
    ?player a cs2:Player .
    OPTIONAL { ?player foaf:nick ?nick . }
    ?player cs2:rating ?rating .
    ?player cs2:kills_per_death ?kills_per_death .
    ?player cs2:headshot_percentage ?headshot_percentage .
    ?player cs2:damage_per_round ?damage_per_round .
    ?player cs2:assists_per_round ?assists_per_round .
    FILTER(?rating > 1.1 && ?kills_per_death > 1.0 && ?headshot_percentage > 45 && ?damage_per_round > 75)
}
ORDER BY DESC(?rating)
"""
run_query(query10, "")

