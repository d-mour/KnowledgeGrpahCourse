Перед запросами, возможно, нужно добавить:
```sparql
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX fr:   <http://example.org/film-rating#>
```

# Графы знаний: компетентносные вопросы

1) Какие режиссёры в конкретном жанре были кассовыми в конкретном году?
```sparql
# 1. Кассовые режиссёры
SELECT ?director ?directorName ?genreLabel
       (SUM(?revenue) AS ?totalRevenue)
       (COUNT(DISTINCT ?movie) AS ?movieCount)
WHERE {
  ?movie a fr:Movie ;
         fr:hasGenre ?genre ;
         fr:revenue ?revenue ;
         fr:releaseDate ?date ;
         fr:directedBy ?director .

  ?genre fr:label ?genreLabel .
  FILTER(CONTAINS(LCASE(?genreLabel), "action"))

  BIND (YEAR(?date) AS ?year)
  FILTER (?year = 2009)

  ?director fr:label ?directorName
}
GROUP BY ?director ?directorName ?genreLabel
ORDER BY DESC(?totalRevenue)
LIMIT 10

```
2) Какие актёры в заданном жанре регулярно появлялись в высокооценённых фильмах в течение определённого промежутка времени?
```sparql
# 2. Актёры в высокооценённых фильмах (более гибкие критерии)
SELECT ?actor ?actorName ?genreLabel
       (COUNT(DISTINCT ?movie) AS ?highRatedMovieCount)
       (AVG(?rating) AS ?avgRating)
WHERE {
  ?movie a fr:Movie ;
         fr:hasGenre ?genre ;
         fr:voteAverage ?rating ;
         fr:releaseDate ?date ;
         fr:hasCast ?castRole .

  ?genre fr:label ?genreLabel .
  FILTER(CONTAINS(LCASE(?genreLabel), "drama"))

  BIND (YEAR(?date) AS ?year)
  FILTER (?year >= 2000 && ?year <= 2010)
  FILTER (?rating >= 7.0)  # снизим порог

  ?castRole a fr:CastRole ;
            fr:playedBy ?actor .

  ?actor fr:label ?actorName .
}
GROUP BY ?actor ?actorName ?genreLabel
HAVING (COUNT(DISTINCT ?movie) >= 2)  # снизим до 2 фильмов
ORDER BY DESC(?highRatedMovieCount) DESC(?avgRating)
LIMIT 10
```
3) Какие кино-компании спродюссировали самые кассовые фильмы в конкретный промежуток времени?
```sparql
# 3. Самые кассовые кино-компании
SELECT ?company ?companyName
       (SUM(?revenue) AS ?totalRevenue)
       (COUNT(DISTINCT ?movie) AS ?movieCount)
WHERE {
  ?movie a fr:Movie ;
         fr:producedBy ?company ;
         fr:revenue ?revenue ;
         fr:releaseDate ?date .

  FILTER (?date >= "2005-01-01"^^xsd:date &&
          ?date <= "2010-12-31"^^xsd:date)

  ?company fr:label ?companyName .
}
GROUP BY ?company ?companyName
ORDER BY DESC(?totalRevenue)
LIMIT 10
```
4) Какой язык оригинальной озвучки ассоциирован с наиболее высокими средними рейтингами фильмов в конкретном жанре?
```sparql
# 4. Языки озвучки с высокими рейтингами в Sci-Fi
SELECT ?lang ?langLabel
       (AVG(?rating) AS ?avgRating)
       (COUNT(DISTINCT ?movie) AS ?movieCount)
WHERE {
  ?movie a fr:Movie ;
         fr:hasGenre ?genre ;
         fr:spokenLanguage ?lang ;
         fr:voteAverage ?rating .
         
  ?genre fr:label ?genreLabel .
  FILTER(CONTAINS(LCASE(?genreLabel), "science fiction"))
  
  # Пытаемся получить метку языка, если есть
  OPTIONAL { ?lang fr:label ?langLabel . }
  
  # Если нет метки, используем сам URI
  BIND(COALESCE(?langLabel, STR(?lang)) AS ?langLabel)
}
GROUP BY ?lang ?langLabel
HAVING (COUNT(DISTINCT ?movie) >= 3)
ORDER BY DESC(?avgRating)
LIMIT 10
```
5) Какие режиссёры снимают фильмы с более высокими оценками чем в среднем по жанру
```sparql
# 5. Режиссёры с оценками выше среднего по их жанрам (оптимизированный)
SELECT ?director ?directorName ?genreName
       (AVG(?rating) AS ?directorAvgRating)
       ?genreAvgRating
       (COUNT(DISTINCT ?movie) AS ?directorMovieCount)
WHERE {
  # Подзапрос: средний рейтинг по жанрам
  {
    SELECT ?genre (AVG(?r) AS ?genreAvgRating)
    WHERE {
      ?m a fr:Movie ;
         fr:hasGenre ?genre ;
         fr:voteAverage ?r .
      FILTER(?r > 0)
    }
    GROUP BY ?genre
    HAVING (COUNT(DISTINCT ?m) >= 10)
  }

  # Основной паттерн: фильмы × жанры × режиссёры
  ?movie a fr:Movie ;
         fr:hasGenre ?genre ;
         fr:voteAverage ?rating ;
         fr:directedBy ?director .
  FILTER(?rating > 0)

  ?director fr:label ?directorName .
  ?genre    fr:label ?genreName .
}
GROUP BY ?director ?directorName ?genre ?genreName ?genreAvgRating
HAVING (COUNT(DISTINCT ?movie) >= 2 &&
        AVG(?rating) > ?genreAvgRating)
ORDER BY DESC(AVG(?rating) - ?genreAvgRating)
LIMIT 50
```
6) Какой съёмочный каст чаще всего работает над фильмами с профитностью выше средней?
```sparql
# 6. Сотрудники на высокоприбыльных фильмах
SELECT ?person ?personName
       (COUNT(DISTINCT ?movie) AS ?highProfitMovieCount)
WHERE {

  # === (1) ОДИН маленький подзапрос: посчитали среднюю прибыль ===
  {
    SELECT (AVG(?profitVal) AS ?avgProfit)
    WHERE {
      ?m a fr:Movie ;
         fr:revenue ?rev ;
         fr:budget ?bud .
      FILTER(?rev > 0 && ?bud > 0)

      BIND(xsd:decimal(?rev - ?bud) AS ?profitVal)
    }
  }

  # === (2) ФИЛЬМЫ, прибыль выше средней ===
  ?movie a fr:Movie ;
         fr:revenue ?revenue ;
         fr:budget ?budget ;
         fr:hasCrew ?crewRole .

  FILTER(?revenue > 0 && ?budget > 0)
  BIND(xsd:decimal(?revenue - ?budget) AS ?profitMovie)
  FILTER(?profitMovie > ?avgProfit)

  # === (3) Участники съёмочной группы ===
  ?crewRole fr:creditsPerson ?person .
  ?person fr:label ?personName .
}
GROUP BY ?person ?personName
HAVING(COUNT(DISTINCT ?movie) >= 2)
ORDER BY DESC(?highProfitMovieCount)
LIMIT 10
```
7) Какие жанры, как правило, имеют более длительную продолжительность у коммерчески успешных фильмов, вышедших в определённом году?
```sparql
# 7. Жанры с самой большой продолжительностью фильмов
SELECT ?genre ?genreName
       (AVG(?runtime) AS ?avgRuntime)
       (COUNT(DISTINCT ?movie) AS ?movieCount)
       (SUM(?revenue) AS ?totalRevenue)
WHERE {
  ?movie a fr:Movie ;
         fr:hasGenre ?genre ;
         fr:runtime ?runtime ;
         fr:revenue ?revenue ;
         fr:releaseDate ?date .

  BIND (YEAR(?date) AS ?year)
  FILTER (?year = 2010)
  FILTER (?revenue >= 50000000)  # снизим порог успешности
  FILTER (?runtime > 0)  # исключаем нулевую продолжительность

  ?genre fr:label ?genreName .
}
GROUP BY ?genre ?genreName
HAVING (COUNT(DISTINCT ?movie) >= 2)
ORDER BY DESC(?avgRuntime)
LIMIT 15
```
8) Какие ключевые слова наиболее ассоциированы с лучшими по рейтингу фильмами в конкретный промежуток времени?
```sparql
# 8. Ключевые слова лучших фильмов
SELECT ?keyword ?keywordLabel
       (COUNT(DISTINCT ?movie) AS ?movieCount)
       (AVG(?rating) AS ?avgRating)
WHERE {
  ?movie a fr:Movie ;
         fr:hasKeyword ?keyword ;
         fr:voteAverage ?rating ;
         fr:releaseDate ?date .

  FILTER (?date >= "2000-01-01"^^xsd:date &&
          ?date <= "2010-12-31"^^xsd:date)
  FILTER (?rating >= 7.0)  # снизим порог

  OPTIONAL { ?keyword fr:label ?keywordLabel . }
  FILTER(BOUND(?keywordLabel))  # только ключевые слова с меткой
}
GROUP BY ?keyword ?keywordLabel
HAVING (COUNT(DISTINCT ?movie) >= 3)  # снизим порог
ORDER BY DESC(?movieCount) DESC(?avgRating)
LIMIT 10
```