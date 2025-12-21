import numpy as np
import pandas as pd
import ampligraph
import tensorflow as tf
from rdflib import Graph, Namespace, URIRef, Literal, RDF

from sklearn import metrics

# Загружаем и парсим RDF граф
g = Graph()
g.parse('skins.rdf', format="xml")

print(1)

# SPARQL запрос
query = """
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX ex: <http://example.org/skin#>
SELECT ?skin ?weaponName ?skinName ?skinEnglishName ?floatRange ?rarity ?collection ?operation ?description ?colors ?quality ?maxPrice ?minPrice ?averagePrice
WHERE {
  ?skin rdf:type ex:Skin .
  ?skin ex:weaponName ?weaponName .
  ?skin ex:skinName ?skinName .
  ?skin ex:skinEnglishName ?skinEnglishName .
  ?skin ex:floatRange ?floatRange .
  ?skin ex:rarity ?rarity .
  ?skin ex:collection ?collection .
  ?skin ex:operation ?operation .
  ?skin ex:description ?description .
  ?skin ex:colors ?colors .
  ?skin ex:quality ?quality .
  ?skin ex:maxPrice ?maxPrice .
  ?skin ex:minPrice ?minPrice .
  ?skin ex:averagePrice ?averagePrice .
}
"""

# Выполняем запрос и сразу создаем DataFrame
results = g.query(query)

print(2)

df = pd.DataFrame(results, columns=["skin", "weaponName", "skinName", "skinEnglishName", "floatRange", "rarity", "collection", "operation", "description", "colors", "quality", "maxPrice", "minPrice", "averagePrice"])

# Удаляем строки с пропущенными значениями
# df = df.dropna()

# Преобразуем качество скинов в уникальные идентификаторы
df["quality_id"] = df["quality"].str.replace(" ", "_").str.title()
df["quality_id"] = df["quality_id"].str.replace("Поношенное", "Worn")
df["quality_id"] = df["quality_id"].str.replace("Закаленное в боях", "Battle_worn")
df["quality_id"] = df["quality_id"].str.replace("После полевых испытаний", "Field_tested")
df["quality_id"] = df["quality_id"].str.replace("Немного поношенное", "Slightly_worn")
df["quality_id"] = df["quality_id"].str.replace("Прямо с завода", "Factory_new")

# Создаем идентификаторы для скинов, оружия и коллекций
df["skin_id"] = "Skin_" + df["skinName"].str.replace(" ", "_").str.title()
df["weapon_id"] = "Weapon_" + df["weaponName"].str.replace(" ", "_").str.title()
df["collection_id"] = "Collection_" + df["collection"].str.replace(" ", "_").str.title()

# Создаем тройки (subject, predicate, object) для графа
triples = []
for _, row in df.iterrows():
    skin = (row["skin_id"], "hasWeapon", row["weapon_id"])
    weapon = (row["weapon_id"], "hasSkin", row["skin_id"])
    quality = (row["skin_id"], "hasQuality", row["quality_id"])
    collection = (row["skin_id"], "hasCollection", row["collection_id"])
    triples.extend([skin, weapon, quality, collection])

print(3)

# Преобразуем тройки в DataFrame
triples_df = pd.DataFrame(triples, columns=['subject', 'predicate', 'object'])

# Разделяем данные на обучающую и тестовую выборки
from ampligraph.evaluation import train_test_split_no_unseen
X_train, X_valid = train_test_split_no_unseen(np.array(triples), test_size=255)

# Инициализация модели и обучение
from ampligraph.latent_features import ScoringBasedEmbeddingModel
model = ScoringBasedEmbeddingModel(k=50, eta=5, scoring_type='ComplEx', seed=0)
optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
model.compile(optimizer=optimizer, loss='binary_crossentropy', entity_relation_regularizer=None)
model.fit(X_train, batch_size=int(X_train.shape[0] / 10), epochs=50, verbose=True)

print(4)

# Оценка модели
ranks = model.evaluate(X_valid, use_filter={'train': X_train, 'test': X_valid}, corrupt_side='s,o', verbose=True)

# Вычисляем метрики (MRR, MR, Hits@N)
from ampligraph.evaluation import mr_score, mrr_score, hits_at_n_score
flat_ranks = ranks.flatten()
res_ranks = flat_ranks[flat_ranks > 0]
mr = mr_score(res_ranks)
mrr = mrr_score(res_ranks)
hits_10 = hits_at_n_score(res_ranks, n=10)
hits_3 = hits_at_n_score(res_ranks, n=3)
hits_1 = hits_at_n_score(res_ranks, n=1)

print(5)

# Визуализация эмбеддингов
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text


embeddings_2d = PCA(n_components=2).fit_transform(np.array([i for i in model.entity_embeddings.values()]))
sns.scatterplot(x=embeddings_2d[:, 0], y=embeddings_2d[:, 1])

# Кластеризация с помощью KMeans
from sklearn.cluster import KMeans
clustering_algorithm = KMeans(n_clusters=6, n_init=50, max_iter=500, random_state=0)
clusters = clustering_algorithm.fit_predict(embeddings_2d)

# Визуализация кластеров
sns.scatterplot(x=embeddings_2d[:, 0], y=embeddings_2d[:, 1], hue=clusters, palette='Set2')
plt.title("2D Visualization of Embeddings")
plt.show()

# Оценка кластеризации
from sklearn.metrics import adjusted_rand_score
metrics.adjusted_rand_score(clusters, df["quality_id"])
