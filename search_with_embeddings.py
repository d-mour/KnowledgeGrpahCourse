#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Поиск автомобилей с использованием embeddings

КАК ЭТО РАБОТАЕТ:
1. Загружаем предварительно созданные embeddings всех автомобилей
2. Создаем embedding для вашего запроса (характеристики желаемого автомобиля)
3. Сравниваем embedding запроса со всеми автомобилями
4. Находим наиболее похожие по косинусному сходству
5. Выводим результаты с объяснением, почему они подходят
"""

from owlready2 import *
import numpy as np
import json
import os
from typing import List, Tuple, Optional, Dict
from create_embeddings import load_embeddings, find_similar_vehicles, extract_vehicle_features
from sparql_queries import (
    clean_name_for_display,
    calculate_reliability_score,
    calculate_fuel_efficiency_level,
    calculate_sportiness_level,
    calculate_family_friendliness_score
)


def create_query_embedding(query_features: dict, scaler, embeddings: np.ndarray) -> np.ndarray:
    """
    СОЗДАНИЕ EMBEDDING ДЛЯ ЗАПРОСА
    
    Что делает:
    - Берет желаемые характеристики (например, city_mpg: 30, crash_rating: 5)
    - Заполняет недостающие значения средними
    - Вычисляет производные признаки (avg_mpg, l_per_100km и т.д.)
    - Нормализует все значения (как при создании embeddings)
    - Превращает в вектор того же размера, что и embeddings автомобилей
    
    Аргументы:
        query_features: словарь с желаемыми характеристиками
        scaler: нормализатор (используется тот же, что при создании embeddings)
        embeddings: матрица embeddings (нужна для определения размерности)
    
    Возвращает:
        numpy array - embedding запроса (вектор чисел)
    """
    print("\n" + "="*80)
    print("ШАГ 1: Создание embedding для вашего запроса")
    print("="*80)
    
    # Список всех признаков, которые используются в embeddings
    feature_names = [
        'year', 'engine_hp', 'engine_cylinders', 'city_mpg', 'highway_mpg',
        'msrp', 'popularity', 'crash_rating', 'trunk_volume', 'num_doors',
        'reliability', 'family_score', 'manufacturer_id', 'body_style_id',
        'drive_type_id', 'fuel_type_id', 'efficiency_level', 'sportiness_level',
        'avg_mpg', 'l_per_100km_city', 'l_per_100km_highway',
        'hp_per_cylinder', 'price_per_hp'
    ]
    
    # Значения по умолчанию (средние значения для всех автомобилей)
    default_features = {
        'year': 2015,
        'engine_hp': 150,
        'engine_cylinders': 4,
        'city_mpg': 20.0,
        'highway_mpg': 28.0,
        'msrp': 25000.0,
        'popularity': 1000,
        'crash_rating': 3,
        'trunk_volume': 15.0,
        'num_doors': 4,
        'reliability': 5.0,
        'family_score': 5.0,
        'manufacturer_id': 0,
        'body_style_id': 0,
        'drive_type_id': 0,
        'fuel_type_id': 0,
        'efficiency_level': 3,  # Medium
        'sportiness_level': 3,  # Medium
        'avg_mpg': 24.0,
        'l_per_100km_city': 11.76,
        'l_per_100km_highway': 8.4,
        'hp_per_cylinder': 25.0,
        'price_per_hp': 200.0
    }
    
    print("\n📋 Ваш запрос:")
    for key, value in query_features.items():
        print(f"   {key}: {value}")
    
    # Обновляем значения из запроса пользователя
    for key, value in query_features.items():
        if key in default_features:
            default_features[key] = value
            print(f"   ✓ Установлено {key} = {value}")
    
    # Вычисляем производные признаки на основе указанных
    print("\n🔧 Вычисление производных признаков:")
    
    if 'city_mpg' in query_features or 'highway_mpg' in query_features:
        default_features['avg_mpg'] = (default_features['city_mpg'] + default_features['highway_mpg']) / 2.0
        default_features['l_per_100km_city'] = 235.2 / default_features['city_mpg'] if default_features['city_mpg'] > 0 else 11.76
        default_features['l_per_100km_highway'] = 235.2 / default_features['highway_mpg'] if default_features['highway_mpg'] > 0 else 8.4
        avg_l_per_100km = 235.2 / default_features['avg_mpg'] if default_features['avg_mpg'] > 0 else 9.4
        print(f"   ✓ Средний расход: {avg_l_per_100km:.1f} l/100km")
        print(f"   ✓ Расход в городе: {default_features['l_per_100km_city']:.1f} l/100km")
    
    if 'engine_hp' in query_features and 'engine_cylinders' in query_features:
        default_features['hp_per_cylinder'] = default_features['engine_hp'] / default_features['engine_cylinders'] if default_features['engine_cylinders'] > 0 else 25.0
        print(f"   ✓ Мощность на цилиндр: {default_features['hp_per_cylinder']:.1f} л.с.")
    
    if 'msrp' in query_features and 'engine_hp' in query_features:
        default_features['price_per_hp'] = default_features['msrp'] / default_features['engine_hp'] if default_features['engine_hp'] > 0 else 200.0
        print(f"   ✓ Цена за л.с.: ${default_features['price_per_hp']:.0f}")
    
    # Создаем вектор признаков (в том же порядке, что и при создании embeddings)
    feature_vector = np.array([[default_features[name] for name in feature_names]])
    
    print(f"\n📊 Создан вектор из {len(feature_names)} признаков")
    
    # Нормализуем (используем тот же scaler, что при создании embeddings)
    if hasattr(scaler, 'transform'):
        # sklearn StandardScaler
        normalized = scaler.transform(feature_vector)
        print("   ✓ Нормализовано (StandardScaler)")
    else:
        # Упрощенная нормализация
        normalized = (feature_vector - scaler['mean']) / scaler['std']
        print("   ✓ Нормализовано (упрощенная версия)")
    
    # Приводим к размерности embeddings (если использовался PCA)
    if normalized.shape[1] > embeddings.shape[1]:
        query_embedding = normalized[0, :embeddings.shape[1]]
        print(f"   ✓ Размерность уменьшена: {normalized.shape[1]} → {embeddings.shape[1]}")
    else:
        query_embedding = normalized[0]
    
    print(f"\n✅ Embedding запроса создан: {len(query_embedding)} измерений")
    
    return query_embedding


def search_by_embedding(query_features: dict, embeddings: np.ndarray, 
                       vehicle_index: dict, scaler, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    ПОИСК АВТОМОБИЛЕЙ ПО EMBEDDING ЗАПРОСА
    
    Что делает:
    1. Создает embedding для запроса
    2. Вычисляет косинусное сходство со всеми автомобилями
    3. Сортирует по убыванию сходства
    4. Возвращает топ-k наиболее похожих
    
    Косинусное сходство:
    - Измеряет угол между векторами
    - Диапазон: -1 до 1
    - 1.0 = идентичные (идеальное совпадение)
    - 0.9 = очень похожие
    - 0.7 = похожие
    - 0.5 = средне похожие
    - 0.0 = не похожие
    """
    print("\n" + "="*80)
    print("ШАГ 2: Поиск похожих автомобилей")
    print("="*80)
    
    # Создаем embedding для запроса
    query_embedding = create_query_embedding(query_features, scaler, embeddings)
    
    print(f"\n🔍 Сравниваю ваш запрос с {len(embeddings)} автомобилями...")
    
    # Вычисляем косинусное сходство
    # Формула: cos(θ) = (A · B) / (||A|| * ||B||)
    # Где A - embedding запроса, B - embedding автомобиля
    similarities = np.dot(embeddings, query_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
    )
    
    print(f"   ✓ Вычислено сходство для всех автомобилей")
    print(f"   ✓ Диапазон сходства: {similarities.min():.3f} - {similarities.max():.3f}")
    
    # Получаем топ-k наиболее похожих (сортируем по убыванию)
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    print(f"\n📈 Топ-{top_k} наиболее похожих автомобилей:")
    for i, idx in enumerate(top_indices[:5], 1):
        similarity = similarities[idx]
        print(f"   {i}. Сходство: {similarity:.4f}")
    
    # Создаем обратный индекс (из позиции в матрице → имя автомобиля)
    index_to_vehicle = {v: k for k, v in vehicle_index.items()}
    
    # Формируем результаты: (имя_автомобиля, сходство)
    results = [(index_to_vehicle[idx], float(similarities[idx])) for idx in top_indices]
    
    return results


def search_by_example_vehicle(example_vehicle_name: str, embeddings: np.ndarray,
                              vehicle_index: dict, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    ПОИСК ПОХОЖИХ НА КОНКРЕТНЫЙ АВТОМОБИЛЬ
    
    Что делает:
    1. Находит embedding указанного автомобиля
    2. Сравнивает его со всеми другими
    3. Находит наиболее похожие
    
    Используется когда пользователь говорит:
    "Найди похожие на BMW 3 Series 2016"
    """
    print("\n" + "="*80)
    print("ПОИСК ПОХОЖИХ АВТОМОБИЛЕЙ")
    print("="*80)
    
    if example_vehicle_name not in vehicle_index:
        print(f"❌ Автомобиль '{example_vehicle_name}' не найден в базе")
        return []
    
    vehicle_idx = vehicle_index[example_vehicle_name]
    vehicle_embedding = embeddings[vehicle_idx]
    
    print(f"\n🎯 Ищем похожие на: {clean_name_for_display(example_vehicle_name)}")
    print(f"   Embedding автомобиля: {len(vehicle_embedding)} измерений")
    
    # Вычисляем косинусное сходство со всеми автомобилями
    similarities = np.dot(embeddings, vehicle_embedding) / (
        np.linalg.norm(embeddings, axis=1) * np.linalg.norm(vehicle_embedding)
    )
    
    print(f"   ✓ Сравнено с {len(embeddings)} автомобилями")
    
    # Получаем топ-k (исключая сам автомобиль)
    top_indices = np.argsort(similarities)[::-1][1:top_k+1]
    
    # Создаем обратный индекс
    index_to_vehicle = {v: k for k, v in vehicle_index.items()}
    
    results = [(index_to_vehicle[idx], float(similarities[idx])) for idx in top_indices]
    
    print(f"\n✅ Найдено {len(results)} похожих автомобилей")
    
    return results


def explain_why_match(vehicle, query_features: dict, similarity: float) -> str:
    """
    ОБЪЯСНЯЕТ, ПОЧЕМУ АВТОМОБИЛЬ ПОПАЛ В РЕЗУЛЬТАТЫ
    
    Сравнивает характеристики автомобиля с запросом и объясняет совпадения
    """
    explanations = []
    
    # Проверяем совпадения по ключевым параметрам
    if 'city_mpg' in query_features:
        if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
            vehicle_mpg = float(vehicle.CityMPG)
            vehicle_l = round(235.2 / vehicle_mpg, 1)
            query_mpg = query_features['city_mpg']
            query_l = round(235.2 / query_mpg, 1)
            diff = abs(vehicle_mpg - query_mpg)
            if diff <= 5:
                explanations.append(f"✓ Расход в городе близок к запрошенному ({vehicle_l} vs {query_l} l/100km)")
            elif vehicle_mpg > query_mpg:
                explanations.append(f"✓ Еще более экономичный ({vehicle_l} l/100km)")
    
    if 'crash_rating' in query_features:
        if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
            vehicle_rating = int(vehicle.OverallCrashRating)
            query_rating = query_features['crash_rating']
            if vehicle_rating >= query_rating:
                explanations.append(f"✓ Высокий рейтинг безопасности ({vehicle_rating}/5)")
    
    if 'trunk_volume' in query_features:
        if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume:
            vehicle_trunk = float(vehicle.TrunkVolume)
            query_trunk = query_features['trunk_volume']
            if vehicle_trunk >= query_trunk * 0.8:  # В пределах 20%
                explanations.append(f"✓ Большой багажник ({vehicle_trunk:.1f} куб.фт)")
    
    if 'msrp' in query_features:
        if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
            vehicle_price = float(vehicle.MSRP)
            query_price = query_features['msrp']
            if vehicle_price <= query_price * 1.2:  # В пределах 20%
                explanations.append(f"✓ Цена в пределах бюджета (${vehicle_price:,.0f})")
    
    # Выводимые свойства
    reliability = calculate_reliability_score(vehicle)
    if reliability and 'reliability' in query_features:
        if reliability >= query_features.get('reliability', 5.0) * 0.9:
            explanations.append(f"✓ Высокая надежность ({reliability:.1f}/10)")
    
    family_score = calculate_family_friendliness_score(vehicle)
    if family_score and 'family_score' in query_features:
        if family_score >= query_features.get('family_score', 5.0) * 0.9:
            explanations.append(f"✓ Высокая семейность ({family_score:.1f}/10)")
    
    # Общее объяснение по сходству
    if similarity >= 0.9:
        explanations.append("🎯 Очень похож на ваш запрос!")
    elif similarity >= 0.8:
        explanations.append("👍 Хорошо соответствует запросу")
    elif similarity >= 0.7:
        explanations.append("✓ Похож по большинству характеристик")
    
    return "\n".join(explanations) if explanations else "Найден по общему сходству характеристик"


def display_results(results: List[Tuple[str, float]], onto, query_features: dict = None):
    """
    ВЫВОДИТ РЕЗУЛЬТАТЫ С ПОДРОБНЫМ ОБЪЯСНЕНИЕМ
    
    Показывает:
    - Название автомобиля
    - Сходство (почему он попал в результаты)
    - Характеристики
    - Объяснение совпадений
    """
    print("\n" + "="*80)
    print(f"РЕЗУЛЬТАТЫ ПОИСКА: найдено {len(results)} автомобилей")
    print("="*80)
    
    if not results:
        print("❌ Автомобили не найдены")
        return
    
    for idx, (vehicle_name, similarity) in enumerate(results, 1):
        # Ищем автомобиль по имени (может быть с разными вариантами)
        vehicle = None
        try:
            # Пробуем найти напрямую
            vehicle = onto.search_one(iri=f"*#{vehicle_name}")
            if not vehicle:
                # Пробуем найти через все экземпляры Vehicle
                for v in onto.Vehicle.instances():
                    if v.name == vehicle_name:
                        vehicle = v
                        break
        except:
            pass
        
        if not vehicle:
            print(f"{idx}. {clean_name_for_display(vehicle_name)} - не найден в онтологии")
            continue
        
        print(f"\n{'─'*80}")
        print(f"{idx}. {clean_name_for_display(vehicle_name)}")
        print(f"{'─'*80}")
        
        # Показываем сходство
        similarity_percent = similarity * 100
        if similarity >= 0.9:
            match_level = "🎯 ОТЛИЧНОЕ СОВПАДЕНИЕ"
        elif similarity >= 0.8:
            match_level = "👍 ХОРОШЕЕ СОВПАДЕНИЕ"
        elif similarity >= 0.7:
            match_level = "✓ НЕПЛОХОЕ СОВПАДЕНИЕ"
        else:
            match_level = "○ СРЕДНЕЕ СОВПАДЕНИЕ"
        
        print(f"\n{match_level} (сходство: {similarity:.4f} = {similarity_percent:.1f}%)")
        
        # Объясняем, почему попал в результаты
        if query_features:
            explanation = explain_why_match(vehicle, query_features, similarity)
            if explanation:
                print(f"\n💡 Почему подходит:")
                for line in explanation.split('\n'):
                    print(f"   {line}")
        
        # Основные характеристики
        print(f"\n📊 Характеристики:")
        
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            manufacturer = clean_name_for_display(vehicle.MadeBy[0].name)
            print(f"   Производитель: {manufacturer}")
        
        if hasattr(vehicle, 'Year') and vehicle.Year:
            print(f"   Год: {vehicle.Year}")
        
        if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
            print(f"   Цена: ${vehicle.MSRP:,.0f}")
        
        if hasattr(vehicle, 'EngineHP') and vehicle.EngineHP:
            print(f"   Мощность: {vehicle.EngineHP} л.с.")
        
        if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
            city_l = round(235.2/vehicle.CityMPG, 1)
            print(f"   Расход в городе: {city_l} l/100km")
        
        if hasattr(vehicle, 'HighwayMPG') and vehicle.HighwayMPG:
            hw_l = round(235.2/vehicle.HighwayMPG, 1)
            print(f"   Расход на трассе: {hw_l} l/100km")
        
        if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
            print(f"   Рейтинг безопасности: {vehicle.OverallCrashRating}/5")
        
        if hasattr(vehicle, 'TrunkVolume') and vehicle.TrunkVolume:
            print(f"   Объем багажника: {vehicle.TrunkVolume} куб.фт")
        
        # Выводимые свойства
        reliability = calculate_reliability_score(vehicle)
        if reliability:
            print(f"   ⭐ Надежность: {reliability:.1f}/10")
        
        efficiency = calculate_fuel_efficiency_level(vehicle)
        if efficiency:
            print(f"   ⛽ Экономичность: {efficiency}")
        
        sportiness = calculate_sportiness_level(vehicle)
        if sportiness:
            print(f"   🏎️ Спортивность: {sportiness}")
        
        family_score = calculate_family_friendliness_score(vehicle)
        if family_score:
            print(f"   👨‍👩‍👧‍👦 Семейность: {family_score:.1f}/10")
        
        if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
            body_style = clean_name_for_display(vehicle.StyledAs[0].name)
            print(f"   Тип кузова: {body_style}")


if __name__ == "__main__":
    print("="*80)
    print("ПОИСК АВТОМОБИЛЕЙ С ИСПОЛЬЗОВАНИЕМ EMBEDDINGS")
    print("="*80)
    
    # Загружаем онтологию
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://cars_ontology.owl").load()
    print(f"   ✓ Загружено автомобилей: {len(list(onto.Vehicle.instances()))}")
    
    # Загружаем embeddings
    print("\n📂 Загрузка embeddings...")
    try:
        embeddings, vehicle_index, scaler = load_embeddings()
        print(f"   ✓ Embeddings загружены: {embeddings.shape[0]} автомобилей, {embeddings.shape[1]} измерений")
        print(f"   ✓ Индекс: {len(vehicle_index)} записей")
    except FileNotFoundError as e:
        print(f"   ❌ Ошибка: {e}")
        print("   💡 Запустите сначала: python create_embeddings.py")
        exit(1)
    
    # Пример 1: Поиск по характеристикам
    print("\n" + "="*80)
    print("ПРИМЕР 1: Поиск экономичного семейного автомобиля")
    print("="*80)
    print("\n📝 Запрос: Нужен экономичный семейный автомобиль с высоким рейтингом безопасности")
    
    query_features = {
        'city_mpg': 30.0,      # Высокий расход в городе (экономичный)
        'highway_mpg': 35.0,   # Высокий расход на трассе
        'crash_rating': 5,     # Максимальный рейтинг безопасности
        'trunk_volume': 20.0,  # Большой багажник
        'num_doors': 4,        # 4 двери (удобно для семьи)
        'msrp': 25000.0,       # Бюджет до $25,000
        'family_score': 8.0,   # Высокая семейность
    }
    
    results = search_by_embedding(query_features, embeddings, vehicle_index, scaler, top_k=10)
    display_results(results, onto, query_features)
    
    # Пример 2: Поиск похожих на конкретный автомобиль
    if len(vehicle_index) > 0:
        print("\n" + "="*80)
        print("ПРИМЕР 2: Поиск похожих автомобилей")
        print("="*80)
        
        # Берем первый попавшийся автомобиль для примера
        example_vehicle = list(vehicle_index.keys())[0]
        print(f"\n📝 Запрос: Найди похожие на {clean_name_for_display(example_vehicle)}")
        
        similar = search_by_example_vehicle(example_vehicle, embeddings, vehicle_index, top_k=5)
        display_results(similar, onto)
    
    print("\n" + "="*80)
    print("ПОИСК ЗАВЕРШЕН")
    print("="*80)
    print("\n💡 Как использовать:")
    print("   1. Измените query_features в коде для вашего запроса")
    print("   2. Или используйте search_by_example_vehicle() для поиска похожих")
    print("   3. Результаты отсортированы по сходству (лучшие первыми)")
