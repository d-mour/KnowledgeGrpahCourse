from rdflib import Graph, Namespace

# Подключаем граф
g = Graph()
g.parse("aviation.ttl", format="turtle")

# Пространство имён
NS = Namespace("http://example.org/war_thunder#")


# 1.Какие самолеты относятся к гидропланам и обладают 
# наибольшим бонусом серебряных львов в аркадном режиме?
query_1 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?seaplane ?silverLionBonus
WHERE {
  ?seaplane a ns1:Seaplane ;
              ns1:hasMode ?arcadeMode .
  ?arcadeMode a ns1:arcade ;
              ns1:hasBonuses ?bonuses .
  ?bonuses ns1:silverLionBonus ?silverLionBonus .
}
ORDER BY DESC(?silverLionBonus)
LIMIT 1
"""

# 2.Какие танки доступны для страны Germany в 8-м ранге?
query_2 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vehicle ?type ?price ?rank
WHERE {
    ?vehicle ns1:hasCountry ns1:germany ;       
             ns1:hasType ?type ;             
             ns1:hasPrice ?price ;           
             ns1:hasRank ?rank .             

    FILTER (xsd:integer(STRAFTER(STR(?rank), "#")) = 8)  

    FILTER NOT EXISTS {
        ?type rdfs:subClassOf* ns1:aviation .
    }
}
ORDER BY ?rank
"""

#3.Какая техника на 4 ранге имеет лучшие 
#  бонусы опыта в симуляторном режиме?
query_3 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vehicle ?rank ?expBonus
WHERE {
  ?vehicle ns1:hasRank ?rank ;
           ns1:hasMode ?simulatorMode .
  ?simulatorMode a ns1:simulator ;
                 ns1:hasBonuses ?bonuses .
  ?bonuses ns1:expBonus ?expBonus .
  FILTER (xsd:integer(STRAFTER(STR(?rank), "#")) = 4)  
}
ORDER BY DESC(?expBonus)
LIMIT 1
"""

#4 4.Какие самолеты имеют бонус опыта выше 100% в любом игровом режиме?

query_4 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vehicle ?type ?price ?rank ?expBonus
WHERE {
  ?vehicle ns1:hasType ?type ;
           ns1:hasPrice ?price ;
           ns1:hasRank ?rank .
  ?vehicle ns1:hasMode ?mode .
  ?mode ns1:hasBonuses ?bonuses .
  ?bonuses ns1:expBonus ?expBonus .
  FILTER (xsd:double(STRAFTER(STR(?expBonus), "#")) > 1.0)

  FILTER NOT EXISTS {
      ?type rdfs:subClassOf* ns1:ground .
  }
}
ORDER BY DESC(?expBonus)
LIMIT 25
"""

# 5.Какая техника лучше всего подходит для фарма серебряных львов в аркадном режиме?

query_5 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vehicle ?type ?silverLionBonus
WHERE {
  ?vehicle ns1:hasMode ?arcadeMode ;
           ns1:hasType ?type .
  ?arcadeMode a ns1:arcade ;
               ns1:hasBonuses ?bonuses .
  ?bonuses ns1:silverLionBonus ?silverLionBonus .
}
ORDER BY DESC(?silverLionBonus)
LIMIT 1
"""

# 6.Какая техника страны Japan имеет наилучший бонус опыта в симуляторном режиме?
query_6 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vehicle ?expBonus
WHERE {
  ?vehicle ns1:hasCountry ns1:japan ;
           ns1:hasMode ?simulatorMode .
  ?simulatorMode a ns1:simulator ;
                 ns1:hasBonuses ?bonuses .
  ?bonuses ns1:expBonus ?expBonus .
}
ORDER BY DESC(?expBonus)
LIMIT 4
"""

#7.У какой техники наибольшее количество битв в симуляторном режиме?
query_7 = """
PREFIX ns1: <http://example.org/war_thunder#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

SELECT ?vehicle ?battles
WHERE {
  ?vehicle ns1:hasMode ?simulatorMode .
  ?simulatorMode a ns1:simulator ;
                 ns1:hasStats ?stats .
  ?stats ns1:battles ?battles .
}
ORDER BY DESC(?battles)
LIMIT 4
"""





# Выполняем запросы
results_1 = g.query(query_1)
results_2 = g.query(query_2)
results_3 = g.query(query_3)
results_4 = g.query(query_4)
results_5 = g.query(query_5)
results_6 = g.query(query_6)
results_7 = g.query(query_7)

# Выводим результаты
print("1. Самолеты, относящиеся к гидропланам и имеющие максимальный бонус серебряных львов:")
for row in results_1:
    print(row)

print("\n2. Танки Германии в 8-м ранге:")
for row in results_2:
    print(row)

print("\n3. Техника на 4 ранге с лучшими бонусами опыта в симуляторном режиме:")
for row in results_3:
    print(row)

print("\n4. Самолеты с бонусом опыта выше 100%:")
for row in results_4:
    print(row)

print("\n5. Техника для фарма серебряных львов в аркадном режиме:")
for row in results_5:
    print(row)

print("\n6. Техника страны Япония с наилучшим бонусом опыта в симуляторном режиме:")
for row in results_6:
    print(row)

print("\n7. Техника с наибольшим количеством битв в симуляторном режиме:")
for row in results_7:
    print(row)