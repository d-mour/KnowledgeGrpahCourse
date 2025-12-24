import numpy as np
import pandas as pd
import torch
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, OneHotEncoder
from sklearn.metrics import accuracy_score
from sklearn.dummy import DummyClassifier
from xgboost import XGBClassifier

def prepare_classification_data(model, triples_factory, ontology_df):
    entity_embeddings = model.entity_representations[0]._embeddings.weight.detach().numpy()
    id_to_entity = {v: k for k, v in triples_factory.entity_to_id.items()}
    
    all_entities_data = []
    for entity_id in range(len(entity_embeddings)):
        entity_name = id_to_entity[entity_id]
        all_entities_data.append({
            'entity_name': entity_name,
            'embedding': entity_embeddings[entity_id]
        })
    entities_df = pd.DataFrame(all_entities_data)
    
    valid_accessories = ontology_df[ontology_df['rarity'].notna()].copy()
    name_to_rarity = pd.Series(valid_accessories['rarity'].values, index=valid_accessories['name']).to_dict()
    
    classification_data = []
    for idx, row in entities_df.iterrows():
        entity_name = row['entity_name']
        if entity_name in name_to_rarity:
            classification_data.append({
                'name': entity_name,
                'embedding': row['embedding'],
                'rarity': name_to_rarity[entity_name]
            })
    
    classification_df = pd.DataFrame(classification_data)
    if classification_df.empty:
        raise ValueError("Нет данных для классификации")
    
    X = np.vstack(classification_df['embedding'].values)
    y_raw = classification_df['rarity'].values
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y_raw)
    
    return X, y, classification_df, label_encoder

def split_data_by_family(classification_df, X, y, test_size=0.2):
    families = classification_df['name'].apply(lambda x: x.split('_')[0] if '_' in x else 'Other')
    
    if len(families.unique()) <= 1:
        print("Мало уникальных семейств, используем случайное разделение")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        train_mask = None
        test_mask = None
        return X_train, X_test, y_train, y_test, train_mask, test_mask
    
    unique_families = families.unique()
    
    np.random.seed(42)
    np.random.shuffle(unique_families)
    
    split_idx = int(len(unique_families) * (1 - test_size))
    train_families = set(unique_families[:split_idx])
    test_families = set(unique_families[split_idx:])
    
    train_mask = families.isin(train_families)
    test_mask = families.isin(test_families)
    
    if not train_mask.any() or not test_mask.any():
        print("Не удалось разделить по семействам, используем случайное разделение")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        train_mask = None
        test_mask = None
        return X_train, X_test, y_train, y_test, train_mask, test_mask
    
    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]
    
    return X_train, X_test, y_train, y_test, train_mask, test_mask

def train_xgboost(X_train, X_test, y_train, y_test):
    if len(X_train) == 0:
        raise ValueError("Обучающая выборка пуста")
    
    if len(np.unique(y_train)) < 2:
        raise ValueError("В обучающей выборке только один класс")
    
    model = XGBClassifier(
        random_state=42,
        n_estimators=100,
        max_depth=6,
        objective='multi:softmax',
        num_class=len(np.unique(y_train))
    )
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy, model

def evaluate_most_frequent_baseline(X_train, X_test, y_train, y_test):
    if len(X_train) == 0:
        return 0.0
    
    dummy_clf = DummyClassifier(strategy='most_frequent', random_state=42)
    dummy_clf.fit(X_train, y_train)
    y_pred_dummy = dummy_clf.predict(X_test)
    accuracy_dummy = accuracy_score(y_test, y_pred_dummy)
    return accuracy_dummy

def prepare_one_hot_data(classification_df):
    names_2d = classification_df['name'].values.reshape(-1, 1)
    onehot_encoder = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
    X_onehot = onehot_encoder.fit_transform(names_2d)
    return X_onehot

def evaluate_one_hot_baseline(X_onehot, y, train_mask, test_mask):
    if train_mask is None or test_mask is None:
        X_train, X_test, y_train, y_test = train_test_split(
            X_onehot, y, test_size=0.2, random_state=42, stratify=y
        )
    else:
        X_train = X_onehot[train_mask]
        X_test = X_onehot[test_mask]
        y_train = y[train_mask]
        y_test = y[test_mask]
    
    dummy_clf = DummyClassifier(strategy='most_frequent', random_state=42)
    dummy_clf.fit(X_train, y_train)
    y_pred = dummy_clf.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    return accuracy

def perform_classification_analysis(model, triples_factory, ontology_df):
    print("\n=== КЛАССИФИКАЦИЯ ПО РЕДКОСТИ ===")
    
    X, y, classification_df, label_encoder = prepare_classification_data(model, triples_factory, ontology_df)
    
    print(f"Всего образцов: {len(X)}")
    print(f"Размерность признаков: {X.shape[1]}")
    print(f"Классы: {list(label_encoder.classes_)}")
    
    class_counts = pd.Series(y).value_counts()
    print(f"Распределение: {class_counts.to_dict()}")
    
    X_train, X_test, y_train, y_test, train_mask, test_mask = split_data_by_family(classification_df, X, y)
    
    print(f"\nРазделение данных:")
    print(f"  Обучающая выборка: {len(X_train)}")
    print(f"  Тестовая выборка: {len(X_test)}")
    
    if len(X_train) == 0 or len(X_test) == 0:
        print("ОШИБКА: Не удалось создать выборки для обучения")
        return {
            'accuracy_xgb': 0.0,
            'accuracy_baseline': 0.0,
            'accuracy_onehot': 0.0,
            'xgb_model': None,
            'label_encoder': label_encoder,
            'classification_df': classification_df
        }
    
    try:
        accuracy_xgb, xgb_model = train_xgboost(X_train, X_test, y_train, y_test)
    except Exception as e:
        print(f"Ошибка при обучении XGBoost: {e}")
        accuracy_xgb = 0.0
        xgb_model = None
    
    accuracy_baseline = evaluate_most_frequent_baseline(X_train, X_test, y_train, y_test)
    
    X_onehot = prepare_one_hot_data(classification_df)
    accuracy_onehot = evaluate_one_hot_baseline(X_onehot, y, train_mask, test_mask)
    
    print(f"\n=== РЕЗУЛЬТАТЫ ===")
    print(f"XGBoost (на эмбеддингах): {accuracy_xgb:.3f}")
    print(f"Базовая модель (самый частый класс): {accuracy_baseline:.3f}")
    print(f"Базовая модель (one-hot названия): {accuracy_onehot:.3f}")
    
    improvement_over_baseline = accuracy_xgb - accuracy_baseline
    improvement_over_onehot = accuracy_xgb - accuracy_onehot
    
    print(f"\nУлучшение относительно базовой модели: {improvement_over_baseline:+.3f}")
    print(f"Улучшение относительно one-hot модели: {improvement_over_onehot:+.3f}")
    
    if accuracy_xgb > max(accuracy_baseline, accuracy_onehot):
        print("✓ Модель на эмбеддингах улучшила точность классификации")
    else:
        print("✗ Модель на эмбеддингах не улучшила точность классификации")
    
    return {
        'accuracy_xgb': accuracy_xgb,
        'accuracy_baseline': accuracy_baseline,
        'accuracy_onehot': accuracy_onehot,
        'xgb_model': xgb_model,
        'label_encoder': label_encoder,
        'classification_df': classification_df
    }
    