from rdflib import Graph, Namespace

base_uri = "http://mitrian.org/terraria.owl"
n = Namespace(base_uri)

graph = Graph()
graph.parse("terraria_upd.owl", format="xml")

# Запрос 1: Враги, обитающие в воде
query1 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?enemy_name
WHERE {
  ?enemy a terraria:Enemy .
  ?enemy terraria:livesInBiome <http://mitrian.org/terraria.owl#вода> .
  ?enemy terraria:hasName ?enemy_name .
}
"""
print('\n FIRST QUERY\n')
results1 = graph.query(query1)
for row in results1:
    print(f"Enemy Name: {row['enemy_name']}")

# Запрос 2: Враги, обитающие в том же биоме, что и Скелетрон
query2 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?enemy_name 
WHERE {
  ?boss a terraria:Boss ;
        terraria:hasName "Скелетрон" ; 
        terraria:livesInBiome ?biome .

  ?enemy a terraria:Enemy ;
         terraria:livesInBiome ?biome ;
         terraria:hasName ?enemy_name .
}
"""
print('\n SECOND QUERY\n')

results2 = graph.query(query2)
for row in results2:
    print(f"Enemy Name: {row['enemy_name']}")

# Запрос 3: Руды с редкостью выше 2
query3 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?name ?cost
WHERE {
    ?ore a terraria:Ore .
    ?ore terraria:hasName ?name .
    ?ore terraria:hasSellPrice ?cost .
    ?ore terraria:hasRarity ?rarity .
    FILTER (?rarity > 2)
}
"""
print('\n THIRD QUERY\n')

results3 = graph.query(query3)
for row in results3:
    print(f"Ore Name: {row['name']}, Cost: {row['cost']}")

# Запрос 4: Мечи с уроном больше 3, с лимитом и смещением
query4 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?weapon_name 
WHERE {
    ?weapon a terraria:MeleeWeapon .
    ?weapon terraria:hasName ?name .
    ?weapon terraria:hasDamage ?damage .

    FILTER (?damage > 3)
    BIND (str(?name) AS ?weapon_name)
}
LIMIT 10
OFFSET 10
"""
print('\n FOURTH QUERY\n')

results4 = graph.query(query4)
for row in results4:
    print(f"Weapon Name: {row['weapon_name']}")

query5 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT (str(?name) AS ?weapon_name) (str(?damage) AS ?weapon_damage)
WHERE {
    ?weapon a terraria:MagicWeapon .
    ?weapon terraria:hasName ?name .
    ?weapon terraria:hasDamage ?damage .
    ?weapon terraria:hasChanceCritDamage ?critChance .
}
ORDER BY DESC(?damage)
LIMIT 1
"""
print('\n FIFTH QUERY\n')
results5 = graph.query(query5)
for row in results5:
    print(f"Weapon Name: {row['weapon_name']}, Weapon Damage: {row['weapon_damage']}")

query6 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?boss_name ?loot (str(?health) AS ?boss_health)
WHERE {
    ?boss a terraria:Boss ;
          terraria:hasName ?boss_name ;
          terraria:hasHealth ?health ;
          terraria:hasLoot ?loot .
}
ORDER BY DESC(?health)
LIMIT 1
"""
print("\n SIXTH QUERY\n")
results6 = graph.query(query6)
for row in results6:
    print(f"Boss Name: {row['boss_name']}, Loot: {row['loot']}, Boss Health: {row['boss_health']}")

query6 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?boss_name ?loot (str(?health) AS ?boss_health)
WHERE {
    ?boss a terraria:Boss ;
          terraria:hasName ?boss_name ;
          terraria:hasHealth ?health ;
          terraria:hasLoot ?loot .
}
ORDER BY DESC(?health)
LIMIT 1
"""
results6 = graph.query(query6)
for row in results6:
    print(f"Boss Name: {row['boss_name']}, Loot: {row['loot']}, Boss Health: {row['boss_health']}")

query7 = """
PREFIX terraria: <http://mitrian.org/terraria.owl#>
SELECT ?required_items
WHERE {
    ?boss a terraria:Boss ;
          terraria:hasName "Глаз Ктулху" ;
          terraria:hasRequiredItemsToWin ?required_items .
}
"""
print('\n SEVENTH QUERY\n')
results7 = graph.query(query7)
for row in results7:
    print(f"Required Items: {row['required_items']}")
