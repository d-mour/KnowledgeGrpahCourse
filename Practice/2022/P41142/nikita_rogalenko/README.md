Работа по курсу "Графовые базы знаний"

Выполнил студент группы P41142 Рогаленко Н. А.

Отчет представлен в файле `report.pdf`. Более подробная информация о проекте представлена в `README.md` 

# F1-knowledge-base
Developing knowledge graph for Formula One racing

## Project structure
- `data_extractor` - Python module for automated Formula One racing series data
extraction. See `README.md` in this directory for more information.
- `knowledge-base-data-importer` - Python module for filling existing ontology with data. Also contains filled graph verification using SHACL, VoID generation  and 
some SPARQL requests.
- `graph-embeddings` - Jupyter notebook for graph embeddings generation and predicting links with them.
- `documentation.html` - HTML documentation for ontology generated with pyLODE.
- `report.pdf` - Presentation for this project.
- `ontology.owl` - OWL ontology for Formula One racing (not populated with individuals).
- `ontology-with-individuals.owl` - OWL ontology for Formula One racing (populated with individuals).
- `shapes.ttl` - Turtle file with graph shapes used for SHACL verification.
- `VoID.owl` - VoID generated for ontology.
