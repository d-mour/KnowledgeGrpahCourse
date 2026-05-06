"""embedding_graph.py - пример кода для извлечения триплетов из онтологии,
выполнения обучения модели эмбеддингов (ampligraph) и оценки полученных результатов
python-version==3.9.x
"""

import os
import numpy as np
import pandas as pd

from rdflib import Graph

import tensorflow as tf
import ampligraph
from ampligraph.latent_features import ScoringBasedEmbeddingModel
from ampligraph.latent_features.loss_functions import get as get_loss
from ampligraph.latent_features.regularizers import get as get_regularizer
from ampligraph.evaluation import train_test_split_no_unseen, mr_score, mrr_score, hits_at_n_score

OWL_FILE = 'knowledge_graph.owl'


def main():
    print(f"ampligraph version: {ampligraph.__version__}")
    print(f"TensorFlow version: {tf.__version__}")

    if not os.path.exists(OWL_FILE):
        print(f"Файл {OWL_FILE} не найден! Убедитесь, что путь указан верно.")
        return

    g = Graph()
    g.parse(OWL_FILE, format='application/rdf+xml')
    print("Онтология успешно загружена.")

    triples = []
    for s, p, o in g:
        if o.startswith("http"):
            triples.append((str(s), str(p), str(o)))

    triples = np.array(triples)
    print(f"Всего триплетов для обучения: {len(triples)}")

    X_train, X_test = train_test_split_no_unseen(triples, test_size=200, allow_duplication=True)
    print('Train set size:', X_train.shape)
    print('Test set size:', X_test.shape)

    model = ScoringBasedEmbeddingModel(
        k=100,
        eta=5,
        scoring_type='ComplEx',
        seed=42
    )

    optimizer = tf.keras.optimizers.Adam(learning_rate=1e-4)
    loss = get_loss('multiclass_nll')
    regularizer = get_regularizer('LP', {'p': 3, 'lambda': 1e-5})

    model.compile(
        optimizer=optimizer,
        loss=loss,
        entity_relation_regularizer=regularizer
    )

    model.fit(
        X_train,
        batch_size=int(X_train.shape[0] / 10),
        epochs=50,
        verbose=True
    )

    ranks = model.evaluate(
        X_test,
        use_filter={'train': X_train, 'test': X_test},
        corrupt_side='s,o',
        verbose=True
    )

    flat_ranks = ranks.flatten()
    valid_ranks = flat_ranks[flat_ranks > 0]

    mr = mr_score(valid_ranks)
    mrr = mrr_score(valid_ranks)
    hits_1 = hits_at_n_score(valid_ranks, n=1)
    hits_3 = hits_at_n_score(valid_ranks, n=3)
    hits_10 = hits_at_n_score(valid_ranks, n=10)

    print()
    print("=== Evaluation Results ===")
    print(f"MR  (Mean Rank):        {mr:.2f} (чем меньше, тем лучше)")
    print(f"MRR (Mean Reciprocal Rank): {mrr:.3f} (чем ближе к 1, тем лучше)")
    print(f"Hits@1:                {hits_1:.3f}")
    print(f"Hits@3:                {hits_3:.3f}")
    print(f"Hits@10:               {hits_10:.3f}")

    entities = np.unique(np.concatenate([X_train[:, 0], X_train[:, 2], X_test[:, 0], X_test[:, 2]]))
    entity_embeddings = model.get_embeddings(entities)

    df_emb = pd.DataFrame(entity_embeddings, index=entities)
    df_emb.to_csv("entity_embeddings.csv", header=False)
    print("Эмбеддинги сущностей сохранены в entity_embeddings.csv")

    print("Готово!")


if __name__ == "__main__":
    main()
