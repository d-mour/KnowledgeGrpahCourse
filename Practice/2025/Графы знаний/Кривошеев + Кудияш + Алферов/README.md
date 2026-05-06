# Итоги курса: Скины CS2 и графы знаний

## Тема проекта
Проект посвящён анализу и кластеризации скинов CS2 с использованием графов знаний. Мы обучаем модели, генерируем эмбеддинги скинов, классифицируем их по редкости, а также визуализируем результаты с помощью алгоритмов уменьшения размерности (UMAP) и кластеризации (KMeans).

### Участники
1. **Егор Кудяшев** (Таб. номер: 412982)
2. **Глеб Альферов** (Таб. номер: 361750)
3. **Кирилл Кривошеев** (Таб. номер: 412981)

## Презентация
[Презентация](https://github.com/Steralka/ITMO/blob/main/5%20%D0%A1%D0%B5%D0%BC%D0%B5%D1%81%D1%82%D1%80/%D0%93%D1%80%D0%B0%D1%84%D1%8B%20%D0%B7%D0%BD%D0%B0%D0%BD%D0%B8%D0%B9/Presentation.pdf)

## Онтология
Онтология, используемая в проекте, описывает типы скинов и их редкость. Данные для работы были получены с различных источников. Ссылки на онтологии:

- [CS2 Skins Ontology](https://csfloat.com/db)
- [Wiki - CS.Money](https://wiki.cs.money/ru)
- [Официальный сайт](https://csgoexpert.com/ru/)

Графический вид онтологии
<img width="2061" height="765" alt="image" src="https://github.com/user-attachments/assets/67ce36e4-723d-4b89-8bc4-464d9f9a772e" />
[Код в Protege](https://github.com/Steralka/ITMO/blob/main/5%20%D0%A1%D0%B5%D0%BC%D0%B5%D1%81%D1%82%D1%80/%D0%93%D1%80%D0%B0%D1%84%D1%8B%20%D0%B7%D0%BD%D0%B0%D0%BD%D0%B8%D0%B9/cs2_ontology_full.ttl)


## Комп. вопросы
1. Какие скины имеют наибольший рост стоимости за последние 6 месяцев среди редких предметов? 
- связь Skin – PriceHistory – Rarity – TimePeriod
2. С какими коллекциями связаны скины, демонстрирующие 
наибольший средний прирост стоимости? 
- связь Skin – Collection – PriceDynamics
3. Какие скины пользователи чаще арендуют перед крупными турнирами (например, PGL Major)? 
- связь Skin – Rental – Event
4. Какие скины и какого уровня редкости чаще всего встречаются в инвестиционных портфелях пользователей?
- связь Skin – Rarity – Portfolio – User

## rdfLib
[rdfLib](https://github.com/Steralka/ITMO/blob/main/5%20%D0%A1%D0%B5%D0%BC%D0%B5%D1%81%D1%82%D1%80/%D0%93%D1%80%D0%B0%D1%84%D1%8B%20%D0%B7%D0%BD%D0%B0%D0%BD%D0%B8%D0%B9/rdflib.py)

## SPARQL
```
# CS2 Ontology SPARQL Queries
# Prefixes
PREFIX cs2: <http://example.org/cs2#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

# 1. Все скины и их цены
SELECT ?skin ?price WHERE { ?skin a cs2:Skin ; cs2:price_usd ?price . } LIMIT 20

# 2. Самые дорогие 10 скинов
SELECT ?skin ?price WHERE { ?skin a cs2:Skin ; cs2:price_usd ?price . } ORDER BY DESC(xsd:decimal(?price)) LIMIT 10

# 3. Все пользователи
SELECT ?user WHERE { ?user a cs2:User . }

# 4. Все транзакции
SELECT ?t WHERE { ?t a cs2:Transaction . }

# 5. Средняя цена всех скинов
SELECT (AVG(xsd:decimal(?price)) AS ?avgPrice) WHERE { ?skin a cs2:Skin ; cs2:price_usd ?price . }

# 6. Средняя прибыль по всем сделкам
SELECT (AVG(xsd:decimal(?profit)) AS ?avgProfit) WHERE { ?s cs2:profit_usd ?profit . }

# 7. Сколько скинов у каждого пользователя
SELECT ?owner (COUNT(?skin) AS ?numSkins) WHERE { ?skin a cs2:Skin ; cs2:owner ?owner . } GROUP BY ?owner ORDER BY DESC(?numSkins)

# 8. Самые редкие скины
SELECT ?skin ?rarity WHERE { ?skin a cs2:Skin ; cs2:rarity ?rarity . FILTER(?rarity = "Covert" || ?rarity = "Classified") }

# 9. Все коллекции и количество скинов
SELECT ?collection (COUNT(?skin) AS ?count) WHERE { ?skin cs2:collection ?collection . } GROUP BY ?collection ORDER BY DESC(?count)

# 10. Сделки с отрицательной прибылью
SELECT ?item ?profit WHERE { ?item cs2:profit_usd ?profit . FILTER(xsd:decimal(?profit) < 0) } ORDER BY ?profit

# 11. Транзакции за ноябрь 2025
SELECT ?t ?date ?owner WHERE { ?t cs2:date ?date ; cs2:owner ?owner . FILTER(STRSTARTS(?date, "2025-11")) }

# 12. Все продажи
SELECT ?t ?price ?owner WHERE { ?t cs2:transaction_type cs2:Transaction_Sale ; cs2:price_usd ?price ; cs2:owner ?owner . } LIMIT 20

# 13. Владельцы самых дорогих скинов
SELECT ?owner (MAX(xsd:decimal(?price)) AS ?maxPrice) WHERE { ?skin cs2:price_usd ?price ; cs2:owner ?owner . } GROUP BY ?owner ORDER BY DESC(?maxPrice) LIMIT 10

# 14. Скины, принадлежащие Ване
SELECT ?skin ?price WHERE { ?skin cs2:owner cs2:User_Vanya ; cs2:price_usd ?price . }

# 15. Прибыль по пользователям
SELECT ?owner (SUM(xsd:decimal(?profit)) AS ?totalProfit) WHERE { ?skin cs2:owner ?owner ; cs2:profit_usd ?profit . } GROUP BY ?owner ORDER BY DESC(?totalProfit)

# 16. Средняя цена по коллекциям
SELECT ?collection (AVG(xsd:decimal(?price)) AS ?avgPrice) WHERE { ?skin cs2:collection ?collection ; cs2:price_usd ?price . } GROUP BY ?collection ORDER BY DESC(?avgPrice)

# 17. Скины с убытком больше 20$
SELECT ?skin ?profit WHERE { ?skin cs2:profit_usd ?profit . FILTER(xsd:decimal(?profit) < -20) }

# 18. Скины без владельца
SELECT ?skin WHERE { ?skin a cs2:Skin . FILTER NOT EXISTS { ?skin cs2:owner ?o } }

# 19. Количество сделок по типам транзакций
SELECT ?type (COUNT(?t) AS ?count) WHERE { ?t cs2:transaction_type ?type . } GROUP BY ?type ORDER BY DESC(?count)

# 20. Самые прибыльные коллекции
SELECT ?collection (SUM(xsd:decimal(?profit)) AS ?totalProfit) WHERE { ?skin cs2:collection ?collection ; cs2:profit_usd ?profit . } GROUP BY ?collection ORDER BY DESC(?totalProfit) LIMIT 10
```

## Embedding
- [Ноутбук](https://drive.google.com/file/d/1G9w91zzO3Hia2Uy69xRUUF1emQdldN7w/view?usp=sharing)

## Заключение

Пройденный курс был полезен для получения знаний в области графов знаний, машинного обучения и анализа данных. Мы научились использовать современные инструменты для работы с графами, таких как PyKEEN, SPARQL, а также алгоритмы кластеризации и визуализации, такие как UMAP и KMeans. Применение этих методов для анализа скинов CS2 продемонстрировало высокую эффективность в решении задач кластеризации и предсказания недостающих связей.


## Используемые технологии
- **rdfLib** — для работы с RDF-данными и создания графов знаний.
- **SPARQL** — для выполнения запросов к данным, представленным в виде графа знаний.
- **PyKEEN** — для обучения моделей графов знаний.
- **UMAP** — для уменьшения размерности данных.
- **KMeans** — для кластеризации скинов.
