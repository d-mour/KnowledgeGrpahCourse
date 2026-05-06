# Граф знаний и эмбеддинги - Dota 2

Выполнили:

* Анкудинов Кирилл
* Волокитин Александр
* Лаврентьев Лев

**Репозиторий:** [https://github.com/lavrentious/kg-dota](https://github.com/lavrentious/kg-dota)

---

## 1. Онтология

**Файл:** [onto-dota.rdf](./onto-dota.rdf)

**[Файл онтологии в репозитории](https://github.com/lavrentious/kg-dota/blob/main/onto-dota.rdf)**

---

## 2. Граф знаний

**Файл:** [kg-dota.rdf](./kg-dota.rdf)

**[Файл графа знаний в репозитории](https://github.com/lavrentious/kg-dota/blob/main/kg-dota.rdf)**

---

## 3. Код построения графа знаний (rdflib)

**Файл:** [builder.py](./builder.py)

**[Основной пакет](https://github.com/lavrentious/kg-dota/tree/main/kg)**

**[Исходный файл в репозитории](https://github.com/lavrentious/kg-dota/blob/main/kg/onto/builder.py)**

### Скрейпинг данных

Используется для извлечения информации о предметах, рецептах и характеристиках.

* [Скрейпер dota2.fandom.com](https://github.com/lavrentious/kg-dota/blob/main/kg/scraper/scrapers/fandom_scraper.py)

### Парсинг и обработка данных

* [Парсер (CLI)](https://github.com/lavrentious/kg-dota/blob/main/kg/parse.py)

* [Примеры SPARQL запросов к графу](https://docs.google.com/document/d/1SER5Q3_LvjH5mSjrVImMsqCGIF4enqaRCUnVh5MxfMA/edit?usp=sharing)

* [Python-запросы к графу](https://github.com/lavrentious/kg-dota/tree/main/kg/queries)

---

## 4. Обучение эмбеддингов

**Файл:** [embedding.ipynb](./embedding.ipynb)

**[Исходный файл в репозитории](https://github.com/lavrentious/kg-dota/blob/main/kg/embedding/main.ipynb)**

---

## 5. Презентация

**Файл:** [presentation.pdf](./presentation.pdf)