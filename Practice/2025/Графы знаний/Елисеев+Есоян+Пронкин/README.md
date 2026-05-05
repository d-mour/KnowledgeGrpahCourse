# Структура проекта

- [презентация.pdf](презентация.pdf): файл с презентацией

- [tmdb_5000_credits.csv](tmdb_5000_credits.csv) и [tmdb_5000_movies.csv](tmdb_5000_movies.csv): исходные данные

- [CQ_&_SPARQL.md](CQ_&_SPARQL.md): Компетентносные вопсросы(CQ) и SPARQL запросы

- [tmdb_schema.ttl](tmdb_schema.ttl): онтология 

- [main.py](main.py): rdflib

- [tmdb_data.ttl](tmdb_data.ttl): тут будет сгенерированная rdflib, заполненная нашими данными онтология

- [sparql.py](sparql/sparql.py): python-скрипт, который запускает наши sparql запросы

- [sparql_result.txt](sparql_result.txt): результат выполнения скрипта [sparql.py](sparql/sparql.py). Он долго выполняется, для защиты сохранил вывод туда. 
