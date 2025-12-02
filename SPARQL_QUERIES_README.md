# SPARQL Запросы для поиска автомобилей

Этот файл содержит SPARQL запросы для поиска автомобилей по различным критериям в онтологии `cars_ontology.owl`.

## Инструкция по использованию в Protege

1. Откройте Protege
2. Загрузите онтологию `cars_ontology.owl` (File → Open)
3. Перейдите на вкладку **SPARQL Query** (в меню Window → Tabs → SPARQL Query)
4. Скопируйте нужный запрос из файла `sparql_queries_for_protege.rq` или из разделов ниже
5. Вставьте запрос в редактор SPARQL
6. Нажмите кнопку **Execute** для выполнения запроса

## Запросы

### Запрос 1: Автомобиль для перевозки детей
**Вопрос:** "Мне нужен автомобиль для перевозки детей, с высоким рейтингом безопасности и большим багажником"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?rating ?trunk ?manufacturer ?year ?price
WHERE {
    ?vehicle rdf:type :Vehicle .
    OPTIONAL { ?vehicle :OverallCrashRating ?rating . }
    OPTIONAL { ?vehicle :TrunkVolume ?trunk . }
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    OPTIONAL { ?vehicle :MSRP ?price . }
    FILTER (
        (!bound(?rating) || ?rating >= 4) &&
        (!bound(?trunk) || ?trunk >= 15.0)
    )
}
ORDER BY DESC(?rating) DESC(?trunk)
LIMIT 20
```

### Запрос 2: Экономичный автомобиль для пробок
**Вопрос:** "Ищу экономичный автомобиль для ежедневных поездок на работу в пробках"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?cityMpg ?highwayMpg ?manufacturer ?year ?price
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :CityMPG ?cityMpg .
    OPTIONAL { ?vehicle :HighwayMPG ?highwayMpg . }
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    OPTIONAL { ?vehicle :MSRP ?price . }
    FILTER (?cityMpg >= 25.0)
}
ORDER BY DESC(?cityMpg)
LIMIT 20
```

### Запрос 3: Спортивные автомобили с ограниченным бюджетом
**Вопрос:** "Люблю скорость, но бюджет ограничен - какие спортивные автомобили доступны?"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?hp ?price ?segment ?manufacturer ?year
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :EngineHP ?hp .
    ?vehicle :MSRP ?price .
    ?vehicle :hasSegment ?segment .
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    FILTER (
        ?hp >= 200 &&
        ?price <= 50000 &&
        (regex(str(?segment), "High-Performance", "i") || 
         regex(str(?segment), "Performance", "i") ||
         regex(str(?segment), "Sport", "i"))
    )
}
ORDER BY DESC(?hp) ASC(?price)
LIMIT 20
```

### Запрос 4: Презентабельный автомобиль для города
**Вопрос:** "Нужен автомобиль для поездок по городу, чтобы выглядеть презентабельно на встречах"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?cityMpg ?segment ?manufacturer ?year ?price
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :hasSegment ?segment .
    ?vehicle :CityMPG ?cityMpg .
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    OPTIONAL { ?vehicle :MSRP ?price . }
    FILTER (
        regex(str(?segment), "Luxury", "i") &&
        ?cityMpg >= 18.0
    )
}
ORDER BY DESC(?cityMpg)
LIMIT 20
```

### Запрос 5: Премиум-класс для спокойной езды
**Вопрос:** "Ищу надежный автомобиль премиум-класса для спокойной езды"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?rating ?segment ?manufacturer ?year ?price
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :hasSegment ?segment .
    OPTIONAL { ?vehicle :OverallCrashRating ?rating . }
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    OPTIONAL { ?vehicle :MSRP ?price . }
    FILTER (
        regex(str(?segment), "Luxury", "i") &&
        (!bound(?rating) || ?rating >= 4)
    )
}
ORDER BY DESC(?rating)
LIMIT 20
```

### Запрос 6: Экономичный для мегаполиса
**Вопрос:** "Живу в мегаполисе с постоянными пробками, нужен экономичный автомобиль"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?cityMpg ?highwayMpg ?manufacturer ?year ?price
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :CityMPG ?cityMpg .
    OPTIONAL { ?vehicle :HighwayMPG ?highwayMpg . }
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    OPTIONAL { ?vehicle :MSRP ?price . }
    FILTER (?cityMpg >= 28.0)
}
ORDER BY DESC(?cityMpg)
LIMIT 20
```

### Запрос 7: Полный привод / Внедорожник
**Вопрос:** "Часто езжу по грунтовым дорогам, нужен автомобиль с полным приводом" / "Живу в селе, дороги плохие, нужен внедорожник или кроссовер"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?driveType ?bodyStyle ?manufacturer ?year ?price
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :DriveType ?driveType .
    OPTIONAL { ?vehicle :StyledAs ?bodyStyle . }
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    OPTIONAL { ?vehicle :MSRP ?price . }
    FILTER (
        (regex(str(?driveType), "all wheel drive", "i") || 
         regex(str(?driveType), "4wd", "i") ||
         regex(str(?driveType), "awd", "i")) &&
        (!bound(?bodyStyle) || 
         regex(str(?bodyStyle), "SUV", "i") ||
         regex(str(?bodyStyle), "Crossover", "i") ||
         regex(str(?bodyStyle), "Wagon", "i"))
    )
}
LIMIT 20
```

### Запрос 8: Бюджет до 20000 с низким расходом
**Вопрос:** "Бюджет до 20000, нужен надежный автомобиль с низким расходом топлива"

```sparql
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX : <http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#>

SELECT DISTINCT ?vehicle ?price ?cityMpg ?highwayMpg ?rating ?manufacturer ?year
WHERE {
    ?vehicle rdf:type :Vehicle .
    ?vehicle :MSRP ?price .
    ?vehicle :CityMPG ?cityMpg .
    ?vehicle :HighwayMPG ?highwayMpg .
    OPTIONAL { ?vehicle :OverallCrashRating ?rating . }
    OPTIONAL { ?vehicle :MadeBy ?manufacturer . }
    OPTIONAL { ?vehicle :Year ?year . }
    FILTER (
        ?price <= 20000 &&
        ?cityMpg >= 25.0 &&
        ?highwayMpg >= 30.0
    )
}
ORDER BY DESC(?cityMpg) DESC(?highwayMpg) DESC(?rating)
LIMIT 20
```

## Примечания

- Все запросы используют префикс `:` для пространства имен онтологии
- Запросы возвращают до 20 результатов, отсортированных по релевантности
- Некоторые свойства могут быть опциональными (OPTIONAL), поэтому не все автомобили могут иметь все значения
- MPG (Miles Per Gallon) - мили на галлон (чем выше, тем экономичнее)
- MSRP - рекомендованная розничная цена в долларах США

