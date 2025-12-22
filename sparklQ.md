1) Какие исполнители выпускали музыку в заданный временной интервал (например, 2010–2015)?


PREFIX mr:  <http://example.org/music_recommendation#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?artist ?year
WHERE {
  ?album a mr:Album ;
         mr:createdBy   ?artist ;
         mr:releaseYear ?year .

  FILTER (
    ?year >= "2010"^^xsd:gYear &&
    ?year <= "2015"^^xsd:gYear
  )
}
ORDER BY ?artist ?year


2) Какие треки были выпущены заданными исполнителями в выбранный временной интервал?
(пример: The Weeknd, Imagine Dragons, Taylor Swift, интервал 2008–2020)

PREFIX mr:  <http://example.org/music_recommendation#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT DISTINCT ?track ?artist ?year
WHERE {
  VALUES ?artist {
    mr:artist_TaylorSwift
    mr:artist_ImagineDragons
    mr:artist_TheWeeknd
    mr:artist_BlackSabbath
  }

  ?album a mr:Album ;
         mr:createdBy ?artist .

  ?track a mr:Track ;
         mr:partOfAlbum ?album ;
         mr:releaseYear ?year .

  FILTER (
    ?year >= "2000"^^xsd:gYear &&
    ?year <= "2020"^^xsd:gYear
  )
}
ORDER BY ?artist ?year ?track


3) Какие жанры чаще всего встречаются среди выбранных исполнителей?
(для тех же трёх исполнителей)

PREFIX mr: <http://example.org/music_recommendation#>

SELECT ?genre (COUNT(DISTINCT ?album) AS ?albumCount)
WHERE {
  VALUES ?artist {
    mr:artist_TaylorSwift
    mr:artist_ImagineDragons
    mr:artist_TheWeeknd
    mr:artist_BlackSabbath
  }

  ?album a mr:Album ;
         mr:createdBy ?artist ;
         mr:hasGenre  ?genre .
}
GROUP BY ?genre
ORDER BY DESC(?albumCount)


4) Какие альбомы или треки можно рекомендовать пользователю, если он выбрал определённый жанр и музыку из конкретного десятилетия?
(пример: жанр Rock и десятилетие 2010-е)

PREFIX mr:  <http://example.org/music_recommendation#>

SELECT DISTINCT ?work ?year
WHERE {
  BIND(mr:genre_pop   AS ?genre)
  BIND(mr:period_2010s AS ?period)

  ?work mr:hasGenre    ?genre ;
        mr:releasedIn  ?period ;
        mr:releaseYear ?year .

  {
    ?work a mr:Album .
  }
  UNION
  {
    ?work a mr:Track .
  }
}
ORDER BY ?year ?work


5) Какие музыкальные работы относятся к тому же жанру, что и выбранное?
(пример: похожие на трек Believer по совпадению жанра)

PREFIX mr: <http://example.org/music_recommendation#>

SELECT DISTINCT ?similarWork ?genre
WHERE {
  mr:track_Amsterdam mr:hasGenre ?genre .

  ?similarWork mr:hasGenre ?genre .

  FILTER (?similarWork != mr:track_Amsterdam)
}
ORDER BY ?similarWork


