# anime-ontology
Список вопросов и SPARQL-запросов

1.	Какие жанры есть у аниме
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?knows_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_relation_knows ?relation .
  ?character ani:dp_name ?name .
  ?relation ani:dp_name ?knows_name
}  
"""

qres = g.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} knows {row.knows_name}")
```
2.	Какие персонажи участвовали в каждом аниме
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?anime_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_character_has_anime ?anime .
  ?character ani:dp_name ?name .
  ?anime ani:dp_name ?anime_name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} in {row.anime_name}")
```

3.	Какие персонажи убили других персонажей
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?kills_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_relation_kills ?relation .
  ?character ani:dp_name ?name .
  ?relation ani:dp_name ?kills_name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} kills {row.kills_name}")
```
4.	Какие персонажи знают друг друга
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?knows_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_relation_knows ?relation .
  ?character ani:dp_name ?name .
  ?relation ani:dp_name ?knows_name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} knows {row.knows_name}")
```
5.	Какой пол у каждого персонажа
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?gender
WHERE
{
  ?character a ani:Character .
  ?character ani:dp_gender_identity ?gender .
  ?character ani:dp_name ?name .
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} has {row.gender}")
```
6.	Какая сущность у каждого персонажа
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?entity
WHERE
{
  ?character a ani:Character .
  ?character ani:dp_entity ?entity .
  ?character ani:dp_name ?name .
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} has {row.entity}")
```
7.	Какие персонажи из аниме с жанром хентай имеют автатарку
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?anime ?character ?id 
WHERE
{
  ani:genre_hentai ani:op_genre_has_anime ?anime .
  ?anime ani:op_anime_has_character ?character .
  ?character ani:dp_gender_identity "female" .
  ?character ani:dp_id ?id .
  ?character ani:dp_picurl ?pic
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.anime} has {row.character} has {row.id}")
```
8.	У каких персонажей есть друзья 
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?friends_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_relation_friends_with ?relation .
  ?character ani:dp_name ?name .
  ?relation ani:dp_name ?friends_name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} friends {row.friends_name}")
```
9.	Какие персонажи аниме проявляют взаимный любовный интерес друг к другу
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?love_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_relation_has_a_love_interest_in ?relation .
  ?relation ani:op_relation_has_a_love_interest_in ?character .
  ?character ani:dp_name ?name .
  ?relation ani:dp_name ?love_name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} love {row.love_name}")
```
10.	Какой персонаж является врагом для других персонажей
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?name ?enemy_name
WHERE
{
  ?character a ani:Character .
  ?character ani:op_relation_is_the_enemy_of ?relation .
  ?relation ani:op_relation_is_the_enemy_of ?character .
  ?character ani:dp_name ?name .
  ?relation ani:dp_name ?enemy_name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} is enemy {row.enemy_name}")
```
11.	Какие аниме озвучил «AniStar»
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?genre ?anime
WHERE
{
  ?genre a ani:Genre .
  ?genre ani:op_genre_has_anime ?anime .
  ?anime ani:dp_fundubber "AniStar" 
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.genre} has {row.anime}")
```
12.	Сколько эпизодов у каждого аниме “ ReZero ” 
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT *
WHERE
{
  ?anime a ani:Anime .
  ?anime ani:dp_episodes ?episode .
  ?anime ani:dp_name "ReZero"
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.episode}")	
```
13.	Какую дату выпуска имеет каждое аниме
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT *
WHERE
{
  ?anime a ani:Anime .
  ?anime ani:dp_aired_on ?aired .
  ?anime ani:dp_name ?name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} {row.aired}")
```
14.	Какое оружие имеет каждый персонаж
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT *
WHERE
{
  ?character a ani:Character .
  ?character ani:dp_weapons ?gun .
  ?character ani:dp_name ?name
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.name} {row.gun}")
```
15.	Какое описание у аниме, которые имеют тип фильм 
```
knows_query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?anime ?description 
WHERE
{
  ?anime a ani:Anime .
  ?anime ani:dp_description ?description  .
  ?anime ani:dp_kind "movie" 
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.anime} has description: {row.description}")
```
16.	Какая продолжительность серий каждого аниме
knows_query = """
```
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX ani: <http://ani.me#>
SELECT ?anime ?duration 
WHERE
{
  ?anime a ani:Anime .
  ?anime ani:dp_duration ?duration  
}  
"""

qres = gg.query(knows_query)
for row in qres:
    #print(row)
    print(f"{row.anime} has description: {row.duration}")
```
