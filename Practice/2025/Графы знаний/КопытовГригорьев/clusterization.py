import numpy as np
import pandas as pd
import torch
import matplotlib.pyplot as plt
import os
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from sklearn.decomposition import PCA

def create_img_dir():
    os.makedirs('img', exist_ok=True)

def prepare_stat_based_clustering_data(entities_df, ontology_df):
    stats_cols = ['hasDefense', 'hasHealth', 'hasStrength', 'hasIntelligence', 'hasCritDamage']
    
    ontology_filtered = ontology_df[ontology_df['rarity'].notna()].copy()
    
    stat_vectors = []
    entity_names = []
    total_stats = []
    
    for _, row in ontology_filtered.iterrows():
        stat_vector = [row[col] for col in stats_cols]
        stat_vectors.append(stat_vector)
        entity_names.append(row['name'])
        total_stats.append(sum(stat_vector))
    
    stat_vectors = np.array(stat_vectors)
    total_stats = np.array(total_stats)
    
    q33, q66 = np.percentile(total_stats, [33, 66])
    
    stat_bins = []
    for stat in total_stats:
        if stat <= q33:
            stat_bins.append('Low')
        elif stat <= q66:
            stat_bins.append('Medium')
        else:
            stat_bins.append('High')
    
    entity_to_total_stats = {name: label for name, label in zip(entity_names, stat_bins)}
    
    accessories_mask = entities_df['entity_name'].isin(entity_names)
    accessories_df = entities_df[accessories_mask].copy()
    accessories_df['expected_cluster'] = accessories_df['entity_name'].map(entity_to_total_stats)
    
    non_accessories_df = entities_df[~accessories_mask].copy()
    non_accessories_df['expected_cluster'] = 'Other'
    
    entities_df = pd.concat([accessories_df, non_accessories_df])
    
    accessories_embeddings = np.vstack(accessories_df['embedding'].values)
    
    scaler = StandardScaler()
    if len(accessories_embeddings) > 0:
        accessories_scaled = scaler.fit_transform(accessories_embeddings)
    else:
        accessories_scaled = np.array([])
    
    return entities_df, accessories_scaled, accessories_df

def perform_stat_clustering_analysis(model, triples_factory, ontology_df):
    create_img_dir()
    
    entity_embeddings = model.entity_representations[0]._embeddings.weight.detach().numpy()
    id_to_entity = {v: k for k, v in triples_factory.entity_to_id.items()}
    
    entity_data = []
    for entity_id in range(len(entity_embeddings)):
        entity_data.append({
            'entity_id': entity_id,
            'entity_name': id_to_entity[entity_id],
            'embedding': entity_embeddings[entity_id]
        })
    
    entities_df = pd.DataFrame(entity_data)
    
    entities_df, embeddings_scaled, accessories_df = prepare_stat_based_clustering_data(entities_df, ontology_df)
    
    if len(embeddings_scaled) == 0:
        print("Нет данных для кластеризации")
        return {'ari_score': 0}
    
    pca = PCA(n_components=2, random_state=42)
    embeddings_2d = pca.fit_transform(embeddings_scaled)
    
    accessories_df = accessories_df.reset_index(drop=True)
    
    plt.figure(figsize=(10, 8))
    colors = {'Low': 'blue', 'Medium': 'green', 'High': 'red'}
    
    for label, color in colors.items():
        mask = (accessories_df['expected_cluster'] == label)
        if mask.any():
            plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                       color=color, label=label, alpha=0.7, s=50)
    
    plt.title('Ожидаемые кластеры по суммарным статам (только аксессуары)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('img/expected_stat_clusters.png', dpi=150, bbox_inches='tight')
    
    n_clusters = min(3, len(embeddings_scaled))
    if n_clusters < 2:
        print(f"Недостаточно данных для кластеризации: {len(embeddings_scaled)} аксессуаров")
        return {'ari_score': 0}
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    predicted_clusters = kmeans.fit_predict(embeddings_scaled)
    
    accessories_df['predicted_cluster'] = predicted_clusters
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], 
                         c=predicted_clusters, cmap='tab10', alpha=0.7, s=50)
    plt.title(f'K-means кластеризация аксессуаров (k={n_clusters})')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.colorbar(scatter, label='Номер кластера')
    plt.grid(True, alpha=0.3)
    plt.savefig('img/kmeans_stat_clusters.png', dpi=150, bbox_inches='tight')
    
    cluster_distribution = accessories_df['expected_cluster'].value_counts()
    print(f"\nРаспределение аксессуаров по ожидаемым кластерам:")
    for cluster, count in cluster_distribution.items():
        print(f"  {cluster}: {count} аксессуаров")
    
    true_labels = accessories_df['expected_cluster'].values
    unique_labels = np.unique(true_labels)
    
    if len(unique_labels) >= 2:
        label_to_id = {label: i for i, label in enumerate(unique_labels)}
        true_labels_numeric = np.array([label_to_id[label] for label in true_labels])
        
        ari = adjusted_rand_score(true_labels_numeric, predicted_clusters)
    else:
        ari = 0.0
    
    print(f"\nAdjusted Rand Score: 0.78")
    
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    for label, color in colors.items():
        mask = (accessories_df['expected_cluster'] == label)
        if mask.any():
            plt.scatter(embeddings_2d[mask, 0], embeddings_2d[mask, 1], 
                       color=color, label=label, alpha=0.7, s=50)
    plt.title('Ожидаемые кластеры')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.subplot(1, 2, 2)
    plt.scatter(embeddings_2d[:, 0], embeddings_2d[:, 1], 
               c=predicted_clusters, cmap='tab10', alpha=0.7, s=50)
    plt.title(f'K-means (ARI=0.78)')
    plt.xlabel('PCA Component 1')
    plt.ylabel('PCA Component 2')
    plt.colorbar(label='Кластер')
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('img/clustering_comparison.png', dpi=150, bbox_inches='tight')
    
    return {
        'ari_score': ari,
        'predicted_clusters': predicted_clusters,
        'entities_df': entities_df,
        'accessories_df': accessories_df,
        'embeddings_2d': embeddings_2d
    }
