#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ЗАДАЧА 7: КЛАССИФИКАЦИЯ С ИСПОЛЬЗОВАНИЕМ KG EMBEDDINGS

Выполняет классификацию автомобилей по типу кузова (BodyStyle)
с использованием векторных представлений.

Сравнивает:
1. Классификацию на основе KG Embeddings
2. Базовую модель (most frequent class)
3. Классификацию на основе one-hot encoding
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
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import LabelEncoder, OneHotEncoder
    from sklearn.metrics import accuracy_score, classification_report
    from sklearn.linear_model import LogisticRegression
    from sklearn.ensemble import RandomForestClassifier
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("❌ sklearn не установлен. Установите: pip install scikit-learn")

try:
    from xgboost import XGBClassifier
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    print("⚠️ xgboost не установлен. Используем RandomForest вместо XGBoost.")


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


def prepare_classification_data(onto, entity_to_id, embeddings, max_samples=3000):
    """Подготовка данных для классификации"""
    print("\n📊 Подготовка данных для классификации...")
    
    vehicle_embeddings = []
    vehicle_names = []
    vehicle_body_styles = []
    vehicle_years = []
    vehicle_manufacturers = []
    
    vehicles = list(onto.Vehicle.instances())[:max_samples]
    
    for vehicle in vehicles:
        if vehicle.name not in entity_to_id:
            continue
        
        if not hasattr(vehicle, 'StyledAs') or not vehicle.StyledAs:
            continue
        
        if not hasattr(vehicle, 'Year') or not vehicle.Year:
            continue
        
        entity_id = entity_to_id[vehicle.name]
        body_style = vehicle.StyledAs[0].name
        year = vehicle.Year
        
        manufacturer = "Unknown"
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            manufacturer = vehicle.MadeBy[0].name
        
        vehicle_embeddings.append(embeddings[entity_id])
        vehicle_names.append(vehicle.name)
        vehicle_body_styles.append(body_style)
        vehicle_years.append(year)
        vehicle_manufacturers.append(manufacturer)
    
    style_counts = {}
    for s in vehicle_body_styles:
        style_counts[s] = style_counts.get(s, 0) + 1
    
    top_styles = sorted(style_counts.items(), key=lambda x: -x[1])[:5]
    top_style_names = [s[0] for s in top_styles]
    
    filtered_embeddings = []
    filtered_names = []
    filtered_styles = []
    filtered_years = []
    filtered_manufacturers = []
    
    for i, style in enumerate(vehicle_body_styles):
        if style in top_style_names:
            filtered_embeddings.append(vehicle_embeddings[i])
            filtered_names.append(vehicle_names[i])
            filtered_styles.append(style)
            filtered_years.append(vehicle_years[i])
            filtered_manufacturers.append(vehicle_manufacturers[i])
    
    print(f"   Всего автомобилей: {len(filtered_embeddings)}")
    print(f"   Классы (типы кузова): {top_style_names}")
    print(f"   Распределение:")
    for s, count in top_styles:
        print(f"      {s}: {count}")
    
    return (np.array(filtered_embeddings), filtered_names, filtered_styles, 
            filtered_years, filtered_manufacturers, top_style_names)


def split_data_by_year(X, y, years, split_year=2015):
    """Разделение данных по году (критерий из пункта 2.3)"""
    print(f"\n📅 Разделение по году (граница: {split_year})...")
    
    train_idx = [i for i, year in enumerate(years) if year < split_year]
    test_idx = [i for i, year in enumerate(years) if year >= split_year]
    
    X_train = X[train_idx]
    X_test = X[test_idx]
    y_train = [y[i] for i in train_idx]
    y_test = [y[i] for i in test_idx]
    
    print(f"   Train (год < {split_year}): {len(X_train)} образцов")
    print(f"   Test (год >= {split_year}): {len(X_test)} образцов")
    
    return X_train, X_test, y_train, y_test


def create_onehot_features(manufacturers, all_manufacturers):
    """Создание one-hot encoding для производителей"""
    manufacturer_to_idx = {m: i for i, m in enumerate(sorted(set(all_manufacturers)))}
    n_manufacturers = len(manufacturer_to_idx)
    
    onehot = np.zeros((len(manufacturers), n_manufacturers))
    for i, m in enumerate(manufacturers):
        if m in manufacturer_to_idx:
            onehot[i, manufacturer_to_idx[m]] = 1
    
    return onehot


def baseline_most_frequent(y_train, y_test):
    """Базовая модель: всегда предсказывает наиболее частый класс"""
    from collections import Counter
    
    most_common = Counter(y_train).most_common(1)[0][0]
    predictions = [most_common] * len(y_test)
    
    return predictions, most_common


def train_and_evaluate(X_train, X_test, y_train, y_test, model_name="KG Embeddings"):
    """Обучение и оценка модели классификации"""
    print(f"\n🔄 Обучение модели ({model_name})...")
    
    le = LabelEncoder()
    y_train_encoded = le.fit_transform(y_train)
    y_test_encoded = le.transform(y_test)
    
    if HAS_XGBOOST:
        clf = XGBClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            use_label_encoder=False,
            eval_metric='mlogloss'
        )
    else:
        clf = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
    
    clf.fit(X_train, y_train_encoded)
    
    y_pred_encoded = clf.predict(X_test)
    y_pred = le.inverse_transform(y_pred_encoded)
    
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"   ✅ Accuracy: {accuracy:.4f} ({accuracy*100:.1f}%)")
    
    return accuracy, y_pred, le


def main():
    """Главная функция"""
    print("="*80)
    print("ЗАДАЧА 7: КЛАССИФИКАЦИЯ С ИСПОЛЬЗОВАНИЕМ KG EMBEDDINGS")
    print("="*80)
    
    if not HAS_PYKEEN or not HAS_SKLEARN:
        print("❌ Отсутствуют необходимые зависимости")
        return
    
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://" + os.path.abspath("cars_ontology.owl")).load()
    print(f"   ✓ Загружено автомобилей: {len(list(onto.Vehicle.instances()))}")
    
    model, entity_to_id, id_to_entity, embeddings = load_model_and_embeddings()
    
    X, names, body_styles, years, manufacturers, style_names = prepare_classification_data(
        onto, entity_to_id, embeddings, max_samples=5000
    )
    
    X_train, X_test, y_train, y_test = split_data_by_year(X, body_styles, years, split_year=2015)
    
    train_idx = [i for i, year in enumerate(years) if year < 2015]
    test_idx = [i for i, year in enumerate(years) if year >= 2015]
    manufacturers_train = [manufacturers[i] for i in train_idx]
    manufacturers_test = [manufacturers[i] for i in test_idx]
    
    print("\n" + "="*80)
    print("МОДЕЛЬ 1: Классификация на основе KG Embeddings")
    print("="*80)
    
    acc_kg, pred_kg, le = train_and_evaluate(X_train, X_test, y_train, y_test, "KG Embeddings")
    
    print("\n" + "="*80)
    print("МОДЕЛЬ 2: Базовая модель (most frequent class)")
    print("="*80)
    
    pred_baseline, most_common = baseline_most_frequent(y_train, y_test)
    acc_baseline = accuracy_score(y_test, pred_baseline)
    print(f"   Наиболее частый класс: {most_common}")
    print(f"   ✅ Accuracy: {acc_baseline:.4f} ({acc_baseline*100:.1f}%)")
    
    print("\n" + "="*80)
    print("МОДЕЛЬ 3: Классификация на основе One-Hot Encoding")
    print("="*80)
    
    X_onehot_train = create_onehot_features(manufacturers_train, manufacturers)
    X_onehot_test = create_onehot_features(manufacturers_test, manufacturers)
    
    print(f"   Размерность one-hot: {X_onehot_train.shape[1]} признаков")
    
    acc_onehot, pred_onehot, _ = train_and_evaluate(
        X_onehot_train, X_onehot_test, y_train, y_test, "One-Hot Encoding"
    )
    
    print("\n" + "="*80)
    print("СРАВНЕНИЕ РЕЗУЛЬТАТОВ")
    print("="*80)
    
    print(f"""
┌────────────────────────────┬────────────┬─────────────┐
│ Модель                     │ Accuracy   │ Улучшение   │
├────────────────────────────┼────────────┼─────────────┤
│ Базовая (most frequent)    │ {acc_baseline*100:>6.1f}%    │    -        │
│ One-Hot Encoding           │ {acc_onehot*100:>6.1f}%    │ {(acc_onehot-acc_baseline)*100:>+5.1f}%     │
│ KG Embeddings              │ {acc_kg*100:>6.1f}%    │ {(acc_kg-acc_baseline)*100:>+5.1f}%     │
└────────────────────────────┴────────────┴─────────────┘
""")
    
    print("📌 Вывод:")
    if acc_kg > acc_baseline:
        improvement = (acc_kg - acc_baseline) * 100
        print(f"   ✅ KG Embeddings улучшили точность на {improvement:.1f}% по сравнению с базовой моделью!")
    else:
        print(f"   ⚠️ KG Embeddings не улучшили точность по сравнению с базовой моделью.")
    
    if acc_kg > acc_onehot:
        improvement = (acc_kg - acc_onehot) * 100
        print(f"   ✅ KG Embeddings лучше One-Hot Encoding на {improvement:.1f}%")
    else:
        diff = (acc_onehot - acc_kg) * 100
        print(f"   ⚠️ One-Hot Encoding лучше KG Embeddings на {diff:.1f}%")
    
    print("\n" + "="*80)
    print("ДЕТАЛЬНЫЙ ОТЧЕТ ПО КЛАССИФИКАЦИИ (KG Embeddings)")
    print("="*80)
    
    from sklearn.metrics import classification_report
    print(classification_report(y_test, pred_kg, target_names=style_names, zero_division=0))


if __name__ == "__main__":
    main()

