# Граф знаний по игре Sid Meier’s Civilization VI

- Кулагин Вячеслав 408946
- Ребрый Егор 409446

## Структура проекта
- `data/*` -- все спарсенные json, которые получены с вики/файлов игры с помощью парсеров
- `parsers/*` -- все используемые парсеры для получения json-файлов
- `to_ontology.py` -- python-файл для превращения json в онтологию, обрабатывая строковые данные
- `Emb_notebook.ipynb` -- ноутбук с эмбедингом. Также доступен в Google Collab по ссылке: [Google Collab Link](https://colab.research.google.com/drive/1RDfEQO_UYOh4wovDQzhLjexsTwk3I3hu?usp=sharing)
- `Presentation.pptx` -- презентация
- Две онтологии: `full` с полным набором сущностей, `empty` -- назполненная