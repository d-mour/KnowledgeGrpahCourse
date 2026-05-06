# Knowledge Graph (RDF/Turtle)

Файл графа: `kg/triples.ttl`.

Граф построен из текущей разметки:
- `annotations/text/entities.tsv`
- `annotations/text/relations.tsv`
- справочников `metadata/*.csv`

Всего сгенерировано **2188** RDF-триплетов.

## 1) Онтология (классы и предикаты)

### Классы
- `ex:Entity`
- `ex:Landmark`
- `ex:Place`
- `ex:Event`
- `ex:Date`
- `ex:Document`
- `ex:Mention`
- `ex:Audio`
- `ex:Image`

### Основные предикаты
- `ex:locatedIn`
- `ex:hasDate`
- `ex:relatedTo`
- `ex:happenedAt`
- `ex:happenedOn`
- `ex:mentions`
- `ex:normalizedEntity`
- `ex:hasPrimaryLandmark`
- `ex:hasAudio`
- `ex:hasImage`

## 2) URI и префиксы

Базовый префикс:
- `ex: <https://example.org/spb-events-dataset/>`

Шаблоны URI:
- Landmark: `ex:landmark/{landmark_id}`
- Place: `ex:place/{place_id}`
- Event: `ex:event/{event_id}`
- Date: `ex:date/{date_iso}`
- Document: `ex:document/{doc_id}`
- Mention: `ex:mention/{doc_id}/{mention_id}`

## 3) Как TSV преобразуется в RDF

### Из `entities.tsv`
- Каждая строка -> узел `ex:Mention`
- `entity_type`/`entity_id` -> ссылка `ex:normalizedEntity` на нормализованный узел (`Landmark/Place/Event/Date`)
- `doc_id` -> `ex:inDocument ex:document/{doc_id}`
- `surface`, `start_char`, `end_char` -> литералы `ex:surface`, `ex:startChar`, `ex:endChar`

Пример:
- TSV: `doc_land_kazan_cathedral_01 m01 LANDMARK land_kazan_cathedral`
- RDF:
  - `ex:mention/doc_land_kazan_cathedral_01/m01 ex:normalizedEntity ex:landmark/land_kazan_cathedral .`

### Из `relations.tsv`
- Каждая строка ->
  1) прямое ребро между нормализованными сущностями (`ex:locatedIn`, `ex:hasDate`, ...)
  2) provenance-узел `ex:relation/{doc_id}/{rel_id}` c `ex:headMention`, `ex:tailMention`, `ex:confidence`

Пример:
- TSV: `LOCATED_IN(m01 -> m02)`
- RDF:
  - `ex:landmark/... ex:locatedIn ex:place/... .`

## 4) Примеры SPARQL-запросов

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

# 1) Все достопримечательности и их русские названия
SELECT ?landmark ?label WHERE {
  ?landmark a ex:Landmark ; rdfs:label ?label .
  FILTER(LANG(?label) = "ru")
}
```

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>

# 2) В каких местах расположены достопримечательности
SELECT ?landmark ?place WHERE {
  ?landmark a ex:Landmark ; ex:locatedIn ?place .
}
```

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>

# 3) События и их даты
SELECT ?event ?date WHERE {
  ?event a ex:Event ; ex:hasDate ?date .
}
```

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>

# 4) События, произошедшие у конкретных ландмарков
SELECT ?event ?landmark WHERE {
  ?event ex:happenedAt ?landmark .
  ?landmark a ex:Landmark .
}
```

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>

# 5) Документы, связанные с Эрмитажем
SELECT ?doc WHERE {
  ?doc a ex:Document ; ex:hasPrimaryLandmark ex:landmark/land_ermitage .
}
```

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>

# 6) Документы и привязанные аудио/изображения
SELECT ?doc ?audio ?image WHERE {
  ?doc a ex:Document .
  OPTIONAL { ?doc ex:hasAudio ?audio . }
  OPTIONAL { ?doc ex:hasImage ?image . }
}
```

```sparql
PREFIX ex: <https://example.org/spb-events-dataset/>

# 7) Provenance: какие mention участвовали в relation
SELECT ?rel ?type ?head ?tail ?conf WHERE {
  ?rel ex:relationType ?type ;
       ex:headMention ?head ;
       ex:tailMention ?tail .
  OPTIONAL { ?rel ex:confidence ?conf . }
}
```
