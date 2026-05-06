# spb-events-dataset

Основной сценарий: человек читает тексты в `raw/text/`, вручную заполняет `annotations/text/entities.tsv` и `annotations/text/relations.tsv`, сверяясь со словарями в `metadata/`.

Подробные правила: [docs/annotation_scheme.md](docs/annotation_scheme.md).

## Минимальная структура

| Путь | Назначение |
| --- | --- |
| `raw/text/` | Нормализованные тексты (`doc_id.txt`) |
| `metadata/docs.csv` | Реестр документов и путей к текстам |
| `metadata/landmarks.csv` | Справочник `LANDMARK` |
| `metadata/places.csv` | Справочник `PLACE` |
| `metadata/events.csv` | Справочник `EVENT` |
| `metadata/relations.csv` | Справочник типов отношений |
| `annotations/text/entities.tsv` | Таблица сущностей |
| `annotations/text/relations.tsv` | Таблица отношений |


- Для каждого `doc_id` используйте тот же `landmark_id`, что в `metadata/docs.csv`.
- Если точный оффсет пока не готов, временно ставьте `start_char=-1`, `end_char=-1` и пояснение в `note`.
- Новые сущности добавляйте в соответствующие справочники `metadata/*.csv` перед финальной валидацией.

## Типы сущностей и отношений

- Сущности: `LANDMARK`, `PLACE`, `DATE`, `EVENT`
- Отношения: `LOCATED_IN`, `HAS_DATE`, `RELATED_TO`, `HAPPENED_AT`, `HAPPENED_ON`