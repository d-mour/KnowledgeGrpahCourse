# Карта проекта: каталоги и файлы

Этот документ описывает назначение каждого каталога и каждого файла, который сейчас лежит в репозитории (без служебного каталога `.git`).

## 1) Каталоги

- `annotations/` - разметка по модальностям (текст, аудио, изображения).
- `annotations/audio/` - аудио-связанный слой разметки.
- `annotations/audio/textgrid/` - файлы выравнивания текста с аудио в формате Praat TextGrid.
- `annotations/images/` - разметка изображений (bounding boxes).
- `annotations/text/` - табличная разметка сущностей и отношений для текста.
- `docs/` - документация по правилам разметки и структуре проекта.
- `kg/` - knowledge graph в RDF/Turtle и пояснения к нему.
- `metadata/` - справочники сущностей, документов, связей с аудио и изображениями.
- `raw/` - исходные данные до преобразования в KG.
- `raw/text/` - нормализованные текстовые фрагменты (`doc_id.txt`) для аннотации.

## 2) Файлы в корне

- `README.md` - краткое описание проекта, минимальной структуры и базового процесса аннотирования.

## 3) Документация

- `docs/annotation_scheme.md` - полная схема разметки: типы сущностей, отношения, оффсеты, контроль качества, экспорт в граф.
- `docs/project_map.md` - этот документ, карта структуры проекта.

## 4) Таблицы разметки текста

- `annotations/text/entities.tsv` - все текстовые упоминания (`mention`) и их нормализация к сущностям (`LANDMARK`, `PLACE`, `EVENT`, `DATE`).
- `annotations/text/relations.tsv` - связи между упоминаниями в рамках `doc_id` (`LOCATED_IN`, `HAS_DATE`, `RELATED_TO`, `HAPPENED_AT`, `HAPPENED_ON`).

## 5) Разметка изображений

- `annotations/images/bbox_annotations.json` - расширенная JSON-разметка bbox по изображениям (связь с `image_id`, `landmark_id`, `doc_ids`, нормализованные координаты).
- `annotations/images/bbox_coco.json` - та же задача детекции в COCO-совместимом формате (`images`, `annotations`, `categories`).

## 6) Метаданные

- `metadata/docs.csv` - реестр документов: `doc_id`, основной `landmark_id`, путь к тексту, привязанные `audio_ids` и `image_ids`.
- `metadata/landmarks.csv` - справочник достопримечательностей (`LANDMARK`) с названиями, районами и Wikidata ID.
- `metadata/places.csv` - справочник локаций (`PLACE`) и иерархии `parent_place_id`.
- `metadata/events.csv` - справочник нормализованных исторических/культурных событий (`EVENT`) и дат.
- `metadata/relations.csv` - справочник допустимых типов отношений и их домен/кодомен.
- `metadata/audio_links.csv` - таблица соответствия аудиофайлов, документов и TextGrid-выравниваний.
- `metadata/image_links.csv` - таблица соответствия изображений, landmark, doc_id и bbox.

## 7) Knowledge Graph

- `kg/README.md` - описание онтологии графа, URI-шаблонов и примеры SPARQL-запросов.
- `kg/triples.ttl` - итоговый RDF/Turtle граф (классы, предикаты, сущности, документы, упоминания, связи, provenance).

## 8) Исходные тексты (`raw/text`)

- `raw/text/doc_land_admiralty_01.txt` - текстовый фрагмент по `land_admiralty` (вариант 01).
- `raw/text/doc_land_admiralty_02.txt` - текстовый фрагмент по `land_admiralty` (вариант 02).
- `raw/text/doc_land_aurora_01.txt` - текстовый фрагмент по `land_aurora` (вариант 01).
- `raw/text/doc_land_aurora_02.txt` - текстовый фрагмент по `land_aurora` (вариант 02).
- `raw/text/doc_land_bronze_horseman_01.txt` - текстовый фрагмент по `land_bronze_horseman` (вариант 01).
- `raw/text/doc_land_bronze_horseman_02.txt` - текстовый фрагмент по `land_bronze_horseman` (вариант 02).
- `raw/text/doc_land_catherine_palace_01.txt` - текстовый фрагмент по `land_catherine_palace` (вариант 01).
- `raw/text/doc_land_catherine_palace_02.txt` - текстовый фрагмент по `land_catherine_palace` (вариант 02).
- `raw/text/doc_land_ermitage_01.txt` - текстовый фрагмент по `land_ermitage` (вариант 01).
- `raw/text/doc_land_ermitage_02.txt` - текстовый фрагмент по `land_ermitage` (вариант 02).
- `raw/text/doc_land_isaak_01.txt` - текстовый фрагмент по `land_isaak` (вариант 01).
- `raw/text/doc_land_isaak_02.txt` - текстовый фрагмент по `land_isaak` (вариант 02).
- `raw/text/doc_land_kazan_cathedral_01.txt` - текстовый фрагмент по `land_kazan_cathedral` (вариант 01).
- `raw/text/doc_land_kazan_cathedral_02.txt` - текстовый фрагмент по `land_kazan_cathedral` (вариант 02).
- `raw/text/doc_land_mariinsky_01.txt` - текстовый фрагмент по `land_mariinsky` (вариант 01).
- `raw/text/doc_land_mariinsky_02.txt` - текстовый фрагмент по `land_mariinsky` (вариант 02).
- `raw/text/doc_land_palace_square_01.txt` - текстовый фрагмент по `land_palace_square` (вариант 01).
- `raw/text/doc_land_palace_square_02.txt` - текстовый фрагмент по `land_palace_square` (вариант 02).
- `raw/text/doc_land_peterhof_palace_01.txt` - текстовый фрагмент по `land_peterhof_palace` (вариант 01).
- `raw/text/doc_land_peterhof_palace_02.txt` - текстовый фрагмент по `land_peterhof_palace` (вариант 02).
- `raw/text/doc_land_peterpaul_01.txt` - текстовый фрагмент по `land_peterpaul` (вариант 01).
- `raw/text/doc_land_peterpaul_02.txt` - текстовый фрагмент по `land_peterpaul` (вариант 02).
- `raw/text/doc_land_rostral_01.txt` - текстовый фрагмент по `land_rostral` (вариант 01).
- `raw/text/doc_land_rostral_02.txt` - текстовый фрагмент по `land_rostral` (вариант 02).
- `raw/text/doc_land_smolny_01.txt` - текстовый фрагмент по `land_smolny` (вариант 01).
- `raw/text/doc_land_smolny_02.txt` - текстовый фрагмент по `land_smolny` (вариант 02).
- `raw/text/doc_land_spilled_blood_01.txt` - текстовый фрагмент по `land_spilled_blood` (вариант 01).
- `raw/text/doc_land_spilled_blood_02.txt` - текстовый фрагмент по `land_spilled_blood` (вариант 02).
- `raw/text/doc_land_summer_garden_01.txt` - текстовый фрагмент по `land_summer_garden` (вариант 01).
- `raw/text/doc_land_summer_garden_02.txt` - текстовый фрагмент по `land_summer_garden` (вариант 02).
- `raw/text/doc_example_001.txt` - учебный/минимальный пример для проверки схемы и оффсетов.

## 9) Аудио-выравнивание (`annotations/audio/textgrid`)

Каждый файл ниже - разметка таймингов для соответствующего текста `doc_id` в формате TextGrid.

- `annotations/audio/textgrid/doc_land_admiralty_01.TextGrid` - выравнивание для `doc_land_admiralty_01`.
- `annotations/audio/textgrid/doc_land_admiralty_02.TextGrid` - выравнивание для `doc_land_admiralty_02`.
- `annotations/audio/textgrid/doc_land_aurora_01.TextGrid` - выравнивание для `doc_land_aurora_01`.
- `annotations/audio/textgrid/doc_land_aurora_02.TextGrid` - выравнивание для `doc_land_aurora_02`.
- `annotations/audio/textgrid/doc_land_bronze_horseman_01.TextGrid` - выравнивание для `doc_land_bronze_horseman_01`.
- `annotations/audio/textgrid/doc_land_bronze_horseman_02.TextGrid` - выравнивание для `doc_land_bronze_horseman_02`.
- `annotations/audio/textgrid/doc_land_catherine_palace_01.TextGrid` - выравнивание для `doc_land_catherine_palace_01`.
- `annotations/audio/textgrid/doc_land_catherine_palace_02.TextGrid` - выравнивание для `doc_land_catherine_palace_02`.
- `annotations/audio/textgrid/doc_land_ermitage_01.TextGrid` - выравнивание для `doc_land_ermitage_01`.
- `annotations/audio/textgrid/doc_land_ermitage_02.TextGrid` - выравнивание для `doc_land_ermitage_02`.
- `annotations/audio/textgrid/doc_land_isaak_01.TextGrid` - выравнивание для `doc_land_isaak_01`.
- `annotations/audio/textgrid/doc_land_isaak_02.TextGrid` - выравнивание для `doc_land_isaak_02`.
- `annotations/audio/textgrid/doc_land_kazan_cathedral_01.TextGrid` - выравнивание для `doc_land_kazan_cathedral_01`.
- `annotations/audio/textgrid/doc_land_kazan_cathedral_02.TextGrid` - выравнивание для `doc_land_kazan_cathedral_02`.
- `annotations/audio/textgrid/doc_land_mariinsky_01.TextGrid` - выравнивание для `doc_land_mariinsky_01`.
- `annotations/audio/textgrid/doc_land_mariinsky_02.TextGrid` - выравнивание для `doc_land_mariinsky_02`.
- `annotations/audio/textgrid/doc_land_palace_square_01.TextGrid` - выравнивание для `doc_land_palace_square_01`.
- `annotations/audio/textgrid/doc_land_palace_square_02.TextGrid` - выравнивание для `doc_land_palace_square_02`.
- `annotations/audio/textgrid/doc_land_peterhof_palace_01.TextGrid` - выравнивание для `doc_land_peterhof_palace_01`.
- `annotations/audio/textgrid/doc_land_peterhof_palace_02.TextGrid` - выравнивание для `doc_land_peterhof_palace_02`.
- `annotations/audio/textgrid/doc_land_peterpaul_01.TextGrid` - выравнивание для `doc_land_peterpaul_01`.
- `annotations/audio/textgrid/doc_land_peterpaul_02.TextGrid` - выравнивание для `doc_land_peterpaul_02`.
- `annotations/audio/textgrid/doc_land_rostral_01.TextGrid` - выравнивание для `doc_land_rostral_01`.
- `annotations/audio/textgrid/doc_land_rostral_02.TextGrid` - выравнивание для `doc_land_rostral_02`.
- `annotations/audio/textgrid/doc_land_smolny_01.TextGrid` - выравнивание для `doc_land_smolny_01`.
- `annotations/audio/textgrid/doc_land_smolny_02.TextGrid` - выравнивание для `doc_land_smolny_02`.
- `annotations/audio/textgrid/doc_land_spilled_blood_01.TextGrid` - выравнивание для `doc_land_spilled_blood_01`.
- `annotations/audio/textgrid/doc_land_spilled_blood_02.TextGrid` - выравнивание для `doc_land_spilled_blood_02`.
- `annotations/audio/textgrid/doc_land_summer_garden_01.TextGrid` - выравнивание для `doc_land_summer_garden_01`.
- `annotations/audio/textgrid/doc_land_summer_garden_02.TextGrid` - выравнивание для `doc_land_summer_garden_02`.
