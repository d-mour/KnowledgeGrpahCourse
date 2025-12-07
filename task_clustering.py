#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЗАДАЧА 6: КЛАСТЕРИЗАЦИЯ С ИСПОЛЬЗОВАНИЕМ KG EMBEDDINGS

Выполняет кластеризацию автомобилей на основе их векторных представлений.
Кластеризация по производителю (Manufacturer).
"""

from owlready2 import *
import os
import json
import numpy as np

try:
    import torch
    from pykeen.models import TransE
    HAS_PYKEEN = True
except ImportError:
    HAS_PYKEEN = False

try:
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.metrics import adjusted_rand_score
    from sklearn.preprocessing import LabelEncoder
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("❌ sklearn не установлен. Установите: pip install scikit-learn")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("⚠️ matplotlib не установлен. Визуализация недоступна.")


def load_model_and_embeddings(model_dir: str = "kg_embeddings_pykeen"):
    """Загружает модель и извлекает embeddings"""
    print("📂 Загрузка модели...")
    
    model_path = os.path.join(model_dir, "trained_model.pkl")
    model = torch.load(model_path, map_location='cpu', weights_only=False)
    
    with open(os.path.join(model_dir, "entity_to_id.json"), 'r') as f:
        entity_to_id = json.load(f)
    
    id_to_entity = {v: k for k, v in entity_to_id.items()}
    
    with torch.no_grad():
        all_entity_ids = torch.arange(model.num_entities, dtype=torch.long)
        embeddings = model.entity_representations[0](all_entity_ids).numpy()
    
    print(f"   ✅ Загружено {len(embeddings)} embeddings размерности {embeddings.shape[1]}")
    
    return model, entity_to_id, id_to_entity, embeddings


def prepare_clustering_data(onto, entity_to_id, embeddings, max_samples=1000):
    """Подготовка данных для кластеризации"""
    print("\n📊 Подготовка данных для кластеризации...")
    
    vehicle_embeddings = []
    vehicle_names = []
    vehicle_manufacturers = []
    
    vehicles = list(onto.Vehicle.instances())[:max_samples]
    
    for vehicle in vehicles:
        if vehicle.name not in entity_to_id:
            continue
        
        if not hasattr(vehicle, 'MadeBy') or not vehicle.MadeBy:
            continue
        
        entity_id = entity_to_id[vehicle.name]
        manufacturer = vehicle.MadeBy[0].name
        
        vehicle_embeddings.append(embeddings[entity_id])
        vehicle_names.append(vehicle.name)
        vehicle_manufacturers.append(manufacturer)
    
    X = np.array(vehicle_embeddings)
    
    top_manufacturers = {}
    for m in vehicle_manufacturers:
        top_manufacturers[m] = top_manufacturers.get(m, 0) + 1
    
    top_5 = sorted(top_manufacturers.items(), key=lambda x: -x[1])[:5]
    top_5_names = [m[0] for m in top_5]
    
    filtered_X = []
    filtered_names = []
    filtered_manufacturers = []
    
    for i, m in enumerate(vehicle_manufacturers):
        if m in top_5_names:
            filtered_X.append(X[i])
            filtered_names.append(vehicle_names[i])
            filtered_manufacturers.append(m)
    
    X = np.array(filtered_X)
    
    print(f"   Всего автомобилей: {len(filtered_X)}")
    print(f"   Производители (топ-5): {top_5_names}")
    print(f"   Распределение:")
    for m, count in top_5:
        print(f"      {m}: {count}")
    
    return X, filtered_names, filtered_manufacturers, top_5_names


def perform_clustering(X, true_labels, n_clusters):
    """Выполнение кластеризации"""
    print(f"\n🔄 Кластеризация KMeans (k={n_clusters})...")
    
    pca = PCA(n_components=2)
    X_2d = pca.fit_transform(X)
    print(f"   PCA: объясненная дисперсия = {sum(pca.explained_variance_ratio_)*100:.1f}%")
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    predicted_labels = kmeans.fit_predict(X)
    
    le = LabelEncoder()
    true_labels_encoded = le.fit_transform(true_labels)
    
    ari = adjusted_rand_score(true_labels_encoded, predicted_labels)
    print(f"   ✅ Adjusted Rand Score: {ari:.4f}")
    
    return X_2d, predicted_labels, true_labels_encoded, ari, le


def visualize_clustering(X_2d, true_labels_encoded, predicted_labels, label_encoder, 
                        true_labels_original, output_prefix="clustering"):
    """Визуализация результатов кластеризации"""
    if not HAS_MATPLOTLIB:
        print("⚠️ matplotlib не установлен, визуализация пропущена")
        return
    
    print("\n📈 Создание визуализаций...")
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    ax1 = axes[0]
    scatter1 = ax1.scatter(X_2d[:, 0], X_2d[:, 1], c=true_labels_encoded, 
                          cmap='tab10', alpha=0.6, s=30)
    ax1.set_title('Ожидаемые кластеры (по производителю)', fontsize=12)
    ax1.set_xlabel('PCA Component 1')
    ax1.set_ylabel('PCA Component 2')
    
    unique_labels = sorted(set(true_labels_original))
    handles1 = [plt.scatter([], [], c=plt.cm.tab10(i/len(unique_labels)), label=label, s=50) 
               for i, label in enumerate(unique_labels)]
    ax1.legend(handles=handles1, title='Производитель', loc='best', fontsize=8)
    
    ax2 = axes[1]
    scatter2 = ax2.scatter(X_2d[:, 0], X_2d[:, 1], c=predicted_labels, 
                          cmap='tab10', alpha=0.6, s=30)
    ax2.set_title('Предсказанные кластеры (KMeans)', fontsize=12)
    ax2.set_xlabel('PCA Component 1')
    ax2.set_ylabel('PCA Component 2')
    
    handles2 = [plt.scatter([], [], c=plt.cm.tab10(i/len(set(predicted_labels))), 
                           label=f'Кластер {i}', s=50) 
               for i in sorted(set(predicted_labels))]
    ax2.legend(handles=handles2, title='Кластер', loc='best', fontsize=8)
    
    plt.tight_layout()
    
    output_file = f"{output_prefix}_results.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"   ✅ Сохранено: {output_file}")
    
    plt.close()


def main():
    """Главная функция"""
    print("="*80)
    print("ЗАДАЧА 6: КЛАСТЕРИЗАЦИЯ С ИСПОЛЬЗОВАНИЕМ KG EMBEDDINGS")
    print("="*80)
    
    if not HAS_PYKEEN or not HAS_SKLEARN:
        print("❌ Отсутствуют необходимые зависимости")
        return
    
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://" + os.path.abspath("cars_ontology.owl")).load()
    print(f"   ✓ Загружено автомобилей: {len(list(onto.Vehicle.instances()))}")
    
    model, entity_to_id, id_to_entity, embeddings = load_model_and_embeddings()
    
    X, vehicle_names, vehicle_manufacturers, top_manufacturers = prepare_clustering_data(
        onto, entity_to_id, embeddings, max_samples=2000
    )
    
    n_clusters = len(top_manufacturers)
    
    X_2d, predicted_labels, true_labels_encoded, ari, label_encoder = perform_clustering(
        X, vehicle_manufacturers, n_clusters
    )
    
    visualize_clustering(
        X_2d, true_labels_encoded, predicted_labels, label_encoder,
        vehicle_manufacturers, output_prefix="clustering"
    )
    
    print("\n" + "="*80)
    print("ИТОГИ КЛАСТЕРИЗАЦИИ")
    print("="*80)
    
    print(f"""
📊 Параметры:
   - Количество кластеров: {n_clusters}
   - Количество объектов: {len(X)}
   - Размерность embeddings: {embeddings.shape[1]}
   - Признак кластеризации: Производитель (Manufacturer)

📈 Метрики качества:
   - Adjusted Rand Score: {ari:.4f}
   
📌 Интерпретация Adjusted Rand Score:
   - ARI = 1.0: идеальное совпадение кластеров
   - ARI = 0.0: случайное распределение
   - ARI > 0.5: хорошая кластеризация
   - ARI > 0.3: умеренная кластеризация
   - ARI < 0.3: слабая кластеризация

✅ Вывод: {"Кластеризация успешна!" if ari > 0.3 else "Кластеризация показывает слабые результаты."}
""")


if __name__ == "__main__":
    main()

