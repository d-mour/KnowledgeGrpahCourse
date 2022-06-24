from ampligraph.evaluation import evaluate_performance
from ampligraph.utils import save_model, restore_model
from rdflib import Graph, URIRef
from ampligraph.evaluation import train_test_split_no_unseen
import numpy as np
import pandas as pd
import tensorflow as tf
from ampligraph.evaluation import mr_score, mrr_score, hits_at_n_score
from ampligraph.latent_features import ComplEx
from ampligraph.discovery import find_clusters
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt
import seaborn as sns
from adjustText import adjust_text
import pickle


def make_triplets():
    ont_uri = "http://www.semanticweb.org/annab/ontologies/2022/3/ontology"
    # Create a Graph
    g = Graph()

    # Parse in an RDF file
    g.parse("./src/resources/graph_resaved.owl")
    triples_list = []

    for subject, predicate, triple_object in g.triples((None, None, None)):
        if predicate.startswith(URIRef(ont_uri)):
            triples_list.append([ent.replace(ont_uri + "#", "bst:") for ent in [subject, predicate, triple_object]])

    df = pd.DataFrame(triples_list, columns=['Subject', 'Predicate', 'Object'])
    print(df)

    return df, triples_list


def split_train_test(triples):
    X_train, X_test = train_test_split_no_unseen(np.array(triples), test_size=2500)
    print('Train set size: ', X_train.shape)
    print('Test set size: ', X_test.shape)
    return X_train, X_test


def build_model(X_train, X_test):
    mdl = ComplEx(batches_count=50,
                  epochs=300,
                  k=100,
                  eta=20,
                  optimizer='adam',
                  optimizer_params={'lr': 1e-4},
                  loss='multiclass_nll',
                  regularizer='LP',
                  regularizer_params={'p': 3, 'lambda': 1e-5},
                  seed=0,
                  verbose=True)

    mdl.fit(X_train)

    filter_triples = np.concatenate((X_train, X_test))
    ranks = evaluate_performance(X_test,
                                 model=mdl,
                                 filter_triples=filter_triples,
                                 use_default_protocol=True,
                                 verbose=True)
    mr = mr_score(ranks)
    mrr = mrr_score(ranks)

    print("MRR: %.2f" % (mrr))
    print("MR: %.2f" % (mr))

    hits_10 = hits_at_n_score(ranks, n=10)
    print("Hits@10: %.2f" % (hits_10))
    hits_3 = hits_at_n_score(ranks, n=3)
    print("Hits@3: %.2f" % (hits_3))
    hits_1 = hits_at_n_score(ranks, n=1)
    print("Hits@1: %.2f" % (hits_1))
    save_model(mdl, model_name_path="./src/resources/my_trained_model")


def clustering(df):

    mdl = restore_model("./src/resources/my_trained_model")
    beasts = df.Subject[df.Subject.str.contains(r'bst:[A-Z].*[^L]')].unique()
    #print(beasts[:1])
    beast_embeddings = dict(zip(beasts, mdl.get_embeddings(beasts)))
    #print(list(beast_embeddings.items())[:1])
    beast_embeddings_array = np.array([i for i in beast_embeddings.values()])
    #print(beast_embeddings_array[:1])

    embeddings_2d = PCA(n_components=2).fit_transform(beast_embeddings_array)

    # Find clusters of embeddings using KMeans
    clustering_algorithm = KMeans(n_clusters=10, n_init=50, max_iter=500, random_state=0)
    clusters = find_clusters(beasts, mdl, clustering_algorithm, mode='entity')

    # Plot results
    df = pd.DataFrame({"beasts": beasts, "clusters": "cluster" + pd.Series(clusters).astype(str),
                       "embedding1": embeddings_2d[:, 0], "embedding2": embeddings_2d[:, 1]})

    plt.figure(figsize=(12, 12))
    plt.title("Cluster embeddings")

    ax = sns.scatterplot(data=df, x="embedding1", y="embedding2", hue="clusters")

    texts = []
    for i, point in df.iterrows():
        if np.random.uniform() < 0.1:
            texts.append(plt.text(point['embedding1'] + .02, point['embedding2'], str(point['beasts'])))
    adjust_text(texts)
    plt.show()
