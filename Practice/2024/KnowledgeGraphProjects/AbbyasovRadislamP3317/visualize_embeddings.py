import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA
import torch

# Загружаем модель
model = torch.load('embedding_output/trained_model.pkl', weights_only=False)

# Загружаем CSV с исходными триплетами
df = pd.read_csv('clean_triples.csv')

# Извлекаем уникальные сущности (из subject и object)
entities = pd.concat([df['subject'], df['object']]).unique()

# Достаём эмбеддинги (по порядку)
entity_embeddings = model.entity_representations[0]().detach().cpu().numpy()

# Проверим соответствие
assert len(entities) == entity_embeddings.shape[0], "Размерности не совпадают!"

# PCA проекция
pca = PCA(n_components=2)
emb_2d = pca.fit_transform(entity_embeddings)

# Визуализация
plt.figure(figsize=(10, 7))
plt.scatter(emb_2d[:, 0], emb_2d[:, 1])

for i, label in enumerate(entities):
    plt.annotate(label, (emb_2d[i, 0], emb_2d[i, 1]), fontsize=8)

plt.title('PCA проекция эмбеддингов сущностей')
plt.grid(True)
plt.tight_layout()
plt.show()
