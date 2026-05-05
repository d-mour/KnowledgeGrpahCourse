from rdflib import Graph
import pandas as pd

# Загружаем граф из OWL
g = Graph()
g.parse("C:/Users/radis/Desktop/Графы Знаний/папка резы/граф_рецептов.owl", format="xml")

print(f"Загружено триплетов: {len(g)}")

triples = []

# Фильтруем только нужные предикаты
keep_predicates = [
    "hasIngredient",
    "belongsToRegion",
    "hasRecipe"
]

prefix = "http://www.semanticweb.org/radis/ontologies/2025/2/untitled-ontology-20#"

for s, p, o in g:
    if any(pred in str(p) for pred in keep_predicates):
        triples.append((
            str(s).replace(prefix, ""), 
            str(p).replace(prefix, ""), 
            str(o).replace(prefix, "")
        ))

df = pd.DataFrame(triples, columns=['subject', 'predicate', 'object'])

# Сохраняем очищенный датасет для PyKEEN
df.to_csv("clean_triples.csv", index=False)
print(df.head(10))
