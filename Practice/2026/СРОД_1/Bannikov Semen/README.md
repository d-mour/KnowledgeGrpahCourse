# Birds Knowledge Graph Project (Labs 1-6)

Проект для выполнения лабораторных работ 1-6 по курсу "Структурирование, разметка и обогащение данных".
Тема: **виды птиц**.

Важно: в проекте используются только реальные источники данных. Разметка выполняется вручную по аннотационной схеме и чеклисту.

## Цель

Собрать мультимодальный набор данных (текст, изображения, аудио) минимум по 10 видам птиц, спроектировать аннотационную схему, выполнить разметку и построить граф знаний.

## Структура репозитория

```text
.
├─ data/
│  ├─ raw/
│  │  ├─ text/
│  │  ├─ images/
│  │  └─ audio/
│  ├─ annotations/
│  │  ├─ text/
│  │  ├─ images/
│  │  └─ audio/
│  ├─ metadata/
│  │  └─ species_catalog.csv
│  └─ README.md
├─ docs/
│  ├─ sources_real_data.md
│  └─ presentation_outline.md
├─ schema/
│  └─ annotation_scheme_template.md
├─ ontology/
│  └─ README.md
├─ notebooks/
│  └─ README.md
├─ scripts/
│  └─ README.md
```

## Минимальные требования по данным (из методички)

- Не менее 10 объектов (видов птиц) в проекте.
- 3 модальности: текст, изображения, аудио.
- Для ЛР4 желательно не менее 30 аудиофайлов в сумме.

## Базовый процесс работы

1. Заполни `data/raw/*` файлами из реальных источников.
2. Веди учет в `data/metadata/species_catalog.csv`.
3. Доработай аннотационную схему в `schema/annotation_scheme_template.md`.
4. Выполняй разметку и складывай результаты в `data/annotations/*`.
5. Для ЛР6 создай онтологию и собери KG (RDF + SPARQL).

## Инструменты (рекомендованные в пособии)

- Текст: WebAnno или INCEpTION.
- Аудио: PRAAT (экспорт TextGrid).
- Изображения: CVAT или Label Studio (JSON/XML).
- KG: Protégé + Python (`rdflib`) + Jupyter.

## Артефакты ЛР6

- Онтология: `ontology/birds_ontology.ttl`
- Экземпляры из разметки: `ontology/birds_instances.ttl`
- Итоговый граф знаний: `ontology/birds_kg.ttl`
- SPARQL-запросы: `ontology/sparql_queries.rq`
- Скрипт сборки KG: `scripts/build_knowledge_graph.py`

