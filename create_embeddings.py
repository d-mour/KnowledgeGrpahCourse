#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Создание векторных представлений (embeddings) для автомобилей
на основе их свойств для семантического поиска
"""

from owlready2 import *
import numpy as np
try:
    from sklearn.preprocessing import StandardScaler
    from sklearn.decomposition import PCA
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("Предупреждение: sklearn не установлен, используется упрощенная версия")
import pickle
import json
from typing import Dict, List, Optional, Tuple
import os

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

# Импортируем функции вычисления свойств из sparql_queries.py
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импортируем функции из sparql_queries
from sparql_queries import (
    calculate_reliability_score,
    calculate_fuel_efficiency_level,
    calculate_sportiness_level,
    calculate_family_friendliness_score
)


def extract_vehicle_features(vehicle) -> Dict:
    """
    Извлекает все признаки автомобиля для создания embedding
    """
    features = {}
    
    # Числовые признаки
    features['year'] = vehicle.Year if hasattr(vehicle, 'Year') and vehicle.Year else 2014
    features['engine_hp'] = vehicle.EngineHP if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP else 150
    features['engine_cylinders'] = vehicle.EngineCylinders if hasattr(vehicle, 'EngineCylinders') and vehicle.EngineCylinders else 4
    features['city_mpg'] = vehicle.CityMPG if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG else 20.0
    features['highway_mpg'] = vehicle.HighwayMPG if hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG else 28.0
    features['msrp'] = vehicle.MSRP if hasattr(vehicle, 'MSRP') and vehicle.MSRP else 25000.0
    features['popularity'] = vehicle.Popularity if hasattr(vehicle, 'Popularity') and vehicle.Popularity else 1000
    features['crash_rating'] = vehicle.OverallCrashRating if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating else 3
    features['trunk_volume'] = vehicle.TrunkVolume if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume else 15.0
    features['num_doors'] = vehicle.NumberOfDoors if hasattr(vehicle, 'NumberOfDoors') and vehicle.NumberOfDoors else 4
    
    # Выводимые свойства
    features['reliability'] = calculate_reliability_score(vehicle) or 5.0
    features['family_score'] = calculate_family_friendliness_score(vehicle) or 5.0
    
    # Категориальные признаки (кодируем как числовые)
    features['manufacturer_id'] = 0
    if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
        manufacturer_name = vehicle.MadeBy[0].name
        # Простое хеширование для производителя
        features['manufacturer_id'] = hash(manufacturer_name) % 100
    
    features['body_style_id'] = 0
    if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
        body_style = vehicle.StyledAs[0].name
        features['body_style_id'] = hash(body_style) % 50
    
    features['drive_type_id'] = 0
    if hasattr(vehicle, 'DriveType') and vehicle.DriveType:
        drive_type = str(vehicle.DriveType)
        if 'all wheel' in drive_type.lower() or 'awd' in drive_type.lower():
            features['drive_type_id'] = 3
        elif 'four wheel' in drive_type.lower() or '4wd' in drive_type.lower():
            features['drive_type_id'] = 2
        elif 'rear wheel' in drive_type.lower():
            features['drive_type_id'] = 1
        else:  # front wheel
            features['drive_type_id'] = 0
    
    features['fuel_type_id'] = 0
    if hasattr(vehicle, 'EngineFuelType') and vehicle.EngineFuelType:
        fuel_type = str(vehicle.EngineFuelType).lower()
        if 'electric' in fuel_type:
            features['fuel_type_id'] = 4
        elif 'diesel' in fuel_type:
            features['fuel_type_id'] = 3
        elif 'premium' in fuel_type:
            features['fuel_type_id'] = 2
        elif 'flex' in fuel_type:
            features['fuel_type_id'] = 1
        else:  # regular
            features['fuel_type_id'] = 0
    
    # Уровни (кодируем как числовые)
    efficiency = calculate_fuel_efficiency_level(vehicle)
    if efficiency == "Very High":
        features['efficiency_level'] = 5
    elif efficiency == "High":
        features['efficiency_level'] = 4
    elif efficiency == "Medium":
        features['efficiency_level'] = 3
    elif efficiency == "Low":
        features['efficiency_level'] = 2
    else:
        features['efficiency_level'] = 1
    
    sportiness = calculate_sportiness_level(vehicle)
    if sportiness == "Very High":
        features['sportiness_level'] = 5
    elif sportiness == "High":
        features['sportiness_level'] = 4
    elif sportiness == "Medium":
        features['sportiness_level'] = 3
    elif sportiness == "Low":
        features['sportiness_level'] = 2
    else:
        features['sportiness_level'] = 1
    
    # Дополнительные вычисляемые признаки
    features['avg_mpg'] = (features['city_mpg'] + features['highway_mpg']) / 2.0
    features['l_per_100km_city'] = 235.2 / features['city_mpg'] if features['city_mpg'] > 0 else 11.76
    features['l_per_100km_highway'] = 235.2 / features['highway_mpg'] if features['highway_mpg'] > 0 else 8.4
    features['hp_per_cylinder'] = features['engine_hp'] / features['engine_cylinders'] if features['engine_cylinders'] > 0 else 25.0
    features['price_per_hp'] = features['msrp'] / features['engine_hp'] if features['engine_hp'] > 0 else 200.0
    
    return features


def create_embeddings(limit: Optional[int] = None, embedding_dim: int = 64) -> Tuple[np.ndarray, Dict[str, int], any]:
    """
    Создает векторные представления для всех автомобилей
    
    Returns:
        embeddings: numpy array с embeddings
        vehicle_index: словарь {vehicle_name: index}
        scaler: StandardScaler для нормализации
    """
    print("="*80)
    print("СОЗДАНИЕ EMBEDDINGS ДЛЯ АВТОМОБИЛЕЙ")
    print("="*80)
    
    vehicles = list(onto.Vehicle.instances())
    
    if limit:
        vehicles = vehicles[:limit]
        print(f"Обработка первых {limit} из {len(onto.Vehicle.instances())} автомобилей...")
    else:
        print(f"Обработка всех {len(vehicles)} автомобилей...")
    
    # Извлекаем признаки для всех автомобилей
    all_features = []
    vehicle_index = {}
    
    for idx, vehicle in enumerate(vehicles):
        if idx % 1000 == 0:
            print(f"Обработано: {idx}/{len(vehicles)}")
        
        features = extract_vehicle_features(vehicle)
        all_features.append(features)
        vehicle_index[vehicle.name] = idx
    
    print(f"\nИзвлечено признаков для {len(all_features)} автомобилей")
    
    # Преобразуем в numpy array
    feature_names = [
        'year', 'engine_hp', 'engine_cylinders', 'city_mpg', 'highway_mpg',
        'msrp', 'popularity', 'crash_rating', 'trunk_volume', 'num_doors',
        'reliability', 'family_score', 'manufacturer_id', 'body_style_id',
        'drive_type_id', 'fuel_type_id', 'efficiency_level', 'sportiness_level',
        'avg_mpg', 'l_per_100km_city', 'l_per_100km_highway',
        'hp_per_cylinder', 'price_per_hp'
    ]
    
    feature_matrix = np.array([[features[name] for name in feature_names] for features in all_features])
    
    print(f"Размерность матрицы признаков: {feature_matrix.shape}")
    
    # Нормализуем признаки
    if HAS_SKLEARN:
        scaler = StandardScaler()
        normalized_features = scaler.fit_transform(feature_matrix)
        print("Признаки нормализованы (StandardScaler)")
    else:
        # Упрощенная нормализация без sklearn
        mean = np.mean(feature_matrix, axis=0)
        std = np.std(feature_matrix, axis=0)
        std[std == 0] = 1  # Избегаем деления на ноль
        normalized_features = (feature_matrix - mean) / std
        scaler = {'mean': mean, 'std': std}
        print("Признаки нормализованы (упрощенная версия)")
    
    # Применяем PCA для уменьшения размерности до embedding_dim
    if HAS_SKLEARN and embedding_dim < normalized_features.shape[1]:
        pca = PCA(n_components=embedding_dim)
        embeddings = pca.fit_transform(normalized_features)
        print(f"Применен PCA: {normalized_features.shape[1]} -> {embedding_dim} измерений")
        print(f"Объясненная дисперсия: {pca.explained_variance_ratio_.sum():.2%}")
    elif embedding_dim < normalized_features.shape[1]:
        # Упрощенное снижение размерности через SVD
        U, s, Vt = np.linalg.svd(normalized_features, full_matrices=False)
        embeddings = U[:, :embedding_dim] * s[:embedding_dim]
        print(f"Применен SVD: {normalized_features.shape[1]} -> {embedding_dim} измерений")
    else:
        embeddings = normalized_features
        print(f"Embeddings без снижения размерности: {embedding_dim} измерений")
    
    print(f"\nСоздано embeddings размерности: {embeddings.shape}")
    
    return embeddings, vehicle_index, scaler


def save_embeddings(embeddings: np.ndarray, vehicle_index: Dict[str, int], 
                   scaler: any, output_dir: str = "embeddings"):
    """Сохраняет embeddings и метаданные"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем embeddings
    embeddings_file = os.path.join(output_dir, "vehicle_embeddings.npy")
    np.save(embeddings_file, embeddings)
    print(f"Embeddings сохранены в {embeddings_file}")
    
    # Сохраняем индекс
    index_file = os.path.join(output_dir, "vehicle_index.json")
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(vehicle_index, f, ensure_ascii=False, indent=2)
    print(f"Индекс сохранен в {index_file}")
    
    # Сохраняем scaler
    scaler_file = os.path.join(output_dir, "scaler.pkl")
    with open(scaler_file, 'wb') as f:
        pickle.dump(scaler, f)
    print(f"Scaler сохранен в {scaler_file}")
    
    # Также сохраняем как JSON для совместимости
    if isinstance(scaler, dict):
        scaler_json_file = os.path.join(output_dir, "scaler.json")
        scaler_json = {
            'mean': scaler['mean'].tolist(),
            'std': scaler['std'].tolist()
        }
        with open(scaler_json_file, 'w') as f:
            json.dump(scaler_json, f)
        print(f"Scaler (JSON) сохранен в {scaler_json_file}")
    
    print(f"\nВсе файлы сохранены в директории: {output_dir}/")


def load_embeddings(embeddings_dir: str = "embeddings") -> Tuple[np.ndarray, Dict[str, int], any]:
    """Загружает embeddings и метаданные"""
    
    embeddings_file = os.path.join(embeddings_dir, "vehicle_embeddings.npy")
    index_file = os.path.join(embeddings_dir, "vehicle_index.json")
    scaler_file = os.path.join(embeddings_dir, "scaler.pkl")
    
    embeddings = np.load(embeddings_file)
    
    with open(index_file, 'r', encoding='utf-8') as f:
        vehicle_index = json.load(f)
    
    try:
        with open(scaler_file, 'rb') as f:
            scaler = pickle.load(f)
    except:
        # Пытаемся загрузить из JSON
        scaler_json_file = os.path.join(embeddings_dir, "scaler.json")
        if os.path.exists(scaler_json_file):
            with open(scaler_json_file, 'r') as f:
                scaler_data = json.load(f)
            scaler = {
                'mean': np.array(scaler_data['mean']),
                'std': np.array(scaler_data['std'])
            }
        else:
            raise FileNotFoundError(f"Не удалось загрузить scaler из {scaler_file}")
    
    return embeddings, vehicle_index, scaler


def find_similar_vehicles(vehicle_name: str, embeddings: np.ndarray, 
                         vehicle_index: Dict[str, int], top_k: int = 10) -> List[Tuple[str, float]]:
    """
    Находит похожие автомобили по embedding
    """
    if vehicle_name not in vehicle_index:
        return []
    
    vehicle_idx = vehicle_index[vehicle_name]
    vehicle_embedding = embeddings[vehicle_idx]
    
    # Вычисляем косинусное сходство со всеми автомобилями
    similarities = np.dot(embeddings, vehicle_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(vehicle_embedding)
    )
    
    # Получаем топ-k наиболее похожих (исключая сам автомобиль)
    top_indices = np.argsort(similarities)[::-1][1:top_k+1]
    
    # Создаем обратный индекс
    index_to_vehicle = {v: k for k, v in vehicle_index.items()}
    
    results = [(index_to_vehicle[idx], float(similarities[idx])) for idx in top_indices]
    
    return results


if __name__ == "__main__":
    import sys
    
    limit = None
    embedding_dim = 64
    
    if len(sys.argv) > 1:
        if '--limit' in sys.argv:
            limit_idx = sys.argv.index('--limit')
            if limit_idx + 1 < len(sys.argv):
                limit = int(sys.argv[limit_idx + 1])
        
        if '--dim' in sys.argv:
            dim_idx = sys.argv.index('--dim')
            if dim_idx + 1 < len(sys.argv):
                embedding_dim = int(sys.argv[dim_idx + 1])
    
    # Создаем embeddings
    embeddings, vehicle_index, scaler = create_embeddings(limit=limit, embedding_dim=embedding_dim)
    
    # Сохраняем
    save_embeddings(embeddings, vehicle_index, scaler)
    
    # Тестируем поиск похожих
    if len(vehicle_index) > 0:
        test_vehicle = list(vehicle_index.keys())[0]
        print(f"\n{'='*80}")
        print(f"ТЕСТ: Поиск похожих на {test_vehicle}")
        print(f"{'='*80}")
        similar = find_similar_vehicles(test_vehicle, embeddings, vehicle_index, top_k=5)
        for vehicle_name, similarity in similar:
            print(f"  {vehicle_name}: {similarity:.4f}")

