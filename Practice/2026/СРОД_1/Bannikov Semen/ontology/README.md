# Ontology

Здесь хранится онтология предметной области "виды птиц" для ЛР6.

## Что добавлено

- `birds_ontology.ttl` - онтология классов/свойств.
- `birds_instances.ttl` - экземпляры, извлеченные из аннотаций.
- `birds_kg.ttl` - объединенный граф (онтология + экземпляры).
- `sparql_queries.rq` - готовые SPARQL-запросы с формулировкой на естественном языке.
- `../scripts/build_knowledge_graph.py` - скрипт сборки графа знаний.

## Как пересобрать граф

```powershell
python scripts/build_knowledge_graph.py
```



