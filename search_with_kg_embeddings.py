#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Поиск автомобилей с использованием Knowledge Graph Embeddings

Использует правильный подход KGE:
- Embeddings для сущностей (Vehicle, Manufacturer, BodyStyle и т.д.)
- Embeddings для отношений (MadeBy, StyledAs, hasSegment и т.д.)
- Поиск через предсказание связей (link prediction)
"""

from owlready2 import *
import numpy as np
import json
import os
from typing import List, Tuple, Optional
from create_kg_embeddings import TransE
from sparql_queries import clean_name_for_display


def load_kg_embeddings(embeddings_dir: str = "kg_embeddings"):
    """
    ЗАГРУЗКА KNOWLEDGE GRAPH EMBEDDINGS
    
    Загружает:
    - Embeddings сущностей
    - Embeddings отношений
    - Индексы (entity_to_id, relation_to_id и обратные)
    - Информацию о модели
    """
    print("="*80)
    print("ЗАГРУЗКА KNOWLEDGE GRAPH EMBEDDINGS")
    print("="*80)
    
    # Загружаем embeddings
    entity_embeddings = np.load(os.path.join(embeddings_dir, "entity_embeddings.npy"))
    relation_embeddings = np.load(os.path.join(embeddings_dir, "relation_embeddings.npy"))
    
    # Загружаем индексы
    with open(os.path.join(embeddings_dir, "entity_to_id.json"), 'r', encoding='utf-8') as f:
        entity_to_id = json.load(f)
    
    with open(os.path.join(embeddings_dir, "relation_to_id.json"), 'r', encoding='utf-8') as f:
        relation_to_id = json.load(f)
    
    with open(os.path.join(embeddings_dir, "id_to_entity.json"), 'r', encoding='utf-8') as f:
        id_to_entity = json.load(f)
        # Конвертируем ключи в int
        id_to_entity = {int(k): v for k, v in id_to_entity.items()}
    
    with open(os.path.join(embeddings_dir, "id_to_relation.json"), 'r', encoding='utf-8') as f:
        id_to_relation = json.load(f)
        id_to_relation = {int(k): v for k, v in id_to_relation.items()}
    
    # Загружаем информацию о модели
    with open(os.path.join(embeddings_dir, "model_info.json"), 'r') as f:
        model_info = json.load(f)
    
    # Создаем модель
    model = TransE(
        num_entities=model_info['num_entities'],
        num_relations=model_info['num_relations'],
        embedding_dim=model_info['embedding_dim']
    )
    model.entity_embeddings = entity_embeddings
    model.relation_embeddings = relation_embeddings
    
    print(f"\n✅ Загружено:")
    print(f"   Сущностей: {len(entity_to_id)}")
    print(f"   Отношений: {len(relation_to_id)}")
    print(f"   Размерность embeddings: {model_info['embedding_dim']}")
    
    return model, entity_to_id, relation_to_id, id_to_entity, id_to_relation


def find_vehicles_by_relation(entity_name: str, relation_name: str,
                              model: TransE, entity_to_id: dict, relation_to_id: dict,
                              id_to_entity: dict, top_k: int = 10,
                              direction: str = "forward") -> List[Tuple[str, float]]:
    """
    ПОИСК АВТОМОБИЛЕЙ ПО СВЯЗИ
    
    Примеры:
    - "Найди все автомобили от BMW" -> direction="backward": (?, MadeBy, BMW)
    - "Найди все седаны" -> direction="backward": (?, StyledAs, Sedan)
    - "Кто производит этот автомобиль?" -> direction="forward": (Vehicle, MadeBy, ?)
    
    Args:
        entity_name: имя сущности (например, "BMW" или "Sedan")
        relation_name: имя отношения (например, "MadeBy" или "StyledAs")
        model: обученная модель TransE
        entity_to_id, relation_to_id: индексы
        id_to_entity: обратный индекс
        top_k: количество результатов
        direction: "forward" для (entity, relation, ?) или "backward" для (?, relation, entity)
    
    Returns:
        List[Tuple[str, float]]: список (имя_сущности, score)
        
    ВАЖНО про Score:
    - Score = -||h + r - t|| (отрицательное расстояние)
    - Чем БЛИЖЕ к 0, тем ЛУЧШЕ (выше score)
    - Отрицательные значения - это нормально!
    - Score -15.9 хуже, чем -1.5 (ближе к 0 = лучше)
    """
    if entity_name not in entity_to_id:
        print(f"❌ Сущность '{entity_name}' не найдена")
        return []
    
    if relation_name not in relation_to_id:
        print(f"❌ Отношение '{relation_name}' не найдено")
        return []
    
    entity_id = entity_to_id[entity_name]
    relation_id = relation_to_id[relation_name]
    
    if direction == "forward":
        # (entity, relation, ?) - предсказываем tail
        print("\n" + "="*80)
        print(f"ПОИСК: ({entity_name}, {relation_name}, ?)")
        print("="*80)
        print(f"   Entity ID: {entity_id}")
        print(f"   Relation ID: {relation_id}")
        print(f"   Ищем: что связано с {entity_name} через {relation_name}")
        
        predictions = model.predict_tail(entity_id, relation_id, top_k=top_k * 3)
    else:
        # (?, relation, entity) - предсказываем head
        print("\n" + "="*80)
        print(f"ПОИСК: (?, {relation_name}, {entity_name})")
        print("="*80)
        print(f"   Entity ID: {entity_id}")
        print(f"   Relation ID: {relation_id}")
        print(f"   Ищем: что связано с {entity_name} через {relation_name} (обратное направление)")
        
        predictions = model.predict_head(relation_id, entity_id, top_k=top_k * 3)
    
    results = []
    for entity_id_pred, score in predictions:
        entity_name_pred = id_to_entity[entity_id_pred]
        # Исключаем саму сущность из результатов (если ищем в обратном направлении)
        if direction == "backward" and entity_id_pred == entity_id:
            continue
        results.append((entity_name_pred, score))
    
    print(f"\n📊 Найдено {len(results)} результатов")
    if results:
        print(f"   Лучший score: {results[0][1]:.4f} (чем ближе к 0, тем лучше)")
        print(f"   Худший score: {results[-1][1]:.4f}")
        if results[0][1] < -10:
            print(f"   ⚠️  ВНИМАНИЕ: Score очень низкий, модель может быть плохо обучена")
            print(f"   💡 Попробуйте переобучить модель с большим количеством эпох")
    
    return results[:top_k]


def find_similar_entities_by_embedding(entity_name: str,
                                      model: TransE, entity_to_id: dict,
                                      id_to_entity: dict, top_k: int = 10) -> List[Tuple[str, float]]:
    """
    ПОИСК ПОХОЖИХ СУЩНОСТЕЙ ПО EMBEDDING
    
    Находит сущности с похожими embeddings (косинусное сходство)
    """
    if entity_name not in entity_to_id:
        return []
    
    entity_id = entity_to_id[entity_name]
    entity_embedding = model.entity_embeddings[entity_id]
    
    # Вычисляем косинусное сходство со всеми сущностями
    similarities = np.dot(model.entity_embeddings, entity_embedding) / (
        np.linalg.norm(model.entity_embeddings, axis=1) * np.linalg.norm(entity_embedding)
    )
    
    # Получаем топ-k (исключая саму сущность)
    top_indices = np.argsort(similarities)[::-1][1:top_k+1]
    
    results = [(id_to_entity[idx], float(similarities[idx])) for idx in top_indices]
    
    return results


def display_kg_results(results: List[Tuple[str, float]], onto, 
                       query_type: str = "relation", entity_name: str = None, relation_name: str = None):
    """
    ВЫВОД РЕЗУЛЬТАТОВ ПОИСКА С ОБЪЯСНЕНИЕМ
    
    Показывает найденные сущности с объяснением, почему они найдены
    """
    print("\n" + "="*80)
    print(f"РЕЗУЛЬТАТЫ ПОИСКА: найдено {len(results)} сущностей")
    print("="*80)
    
    if not results:
        print("❌ Сущности не найдены")
        return
    
    for idx, (entity_name_result, score) in enumerate(results, 1):
        print(f"\n{'─'*80}")
        print(f"{idx}. {clean_name_for_display(entity_name_result)}")
        print(f"{'─'*80}")
        
        # Показываем score
        print(f"\n📊 Score: {score:.4f}")
        print(f"   💡 Score = -||h + r - t|| (отрицательное расстояние)")
        print(f"   💡 Чем БЛИЖЕ к 0, тем ЛУЧШЕ предсказание")
        
        if score > -1.0:
            match_level = "🎯 ОТЛИЧНЫЙ SCORE (очень близко к 0)"
        elif score > -2.0:
            match_level = "👍 ХОРОШИЙ SCORE"
        elif score > -5.0:
            match_level = "✓ СРЕДНИЙ SCORE"
        elif score > -10.0:
            match_level = "○ НИЗКИЙ SCORE"
        else:
            match_level = "❌ ОЧЕНЬ НИЗКИЙ SCORE (модель не уверена)"
        
        print(f"{match_level}")
        
        # Пытаемся найти в онтологии и показать информацию
        vehicle = None
        try:
            # Пробуем найти через поиск
            vehicle = onto.search_one(iri=f"*#{entity_name_result}")
            if not vehicle:
                # Пробуем найти через все экземпляры
                for v in onto.Vehicle.instances():
                    if v.name == entity_name_result:
                        vehicle = v
                        break
        except:
            pass
        
        if vehicle:
            print(f"\n📋 Информация об автомобиле:")
            
            if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
                manufacturer = clean_name_for_display(vehicle.MadeBy[0].name)
                print(f"   Производитель: {manufacturer}")
            
            if hasattr(vehicle, 'Year') and vehicle.Year:
                print(f"   Год: {vehicle.Year}")
            
            if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
                print(f"   Цена: ${vehicle.MSRP:,.0f}")
            
            if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
                body_style = clean_name_for_display(vehicle.StyledAs[0].name)
                print(f"   Тип кузова: {body_style}")
            
            if hasattr(vehicle, 'hasSegment') and vehicle.hasSegment:
                segments = [clean_name_for_display(s.name) for s in vehicle.hasSegment]
                print(f"   Сегменты: {', '.join(segments)}")
            
            if hasattr(vehicle, 'CityMPG') and vehicle.CityMPG:
                city_l = round(235.2/vehicle.CityMPG, 1)
                print(f"   Расход в городе: {city_l} l/100km")
            
            if hasattr(vehicle, 'OverallCrashRating') and vehicle.OverallCrashRating:
                print(f"   Рейтинг безопасности: {vehicle.OverallCrashRating}/5")
        else:
            # Может быть это не Vehicle, а другая сущность
            print(f"\n💡 Это сущность типа: {type(entity_name_result)}")
            print(f"   (не Vehicle, возможно Manufacturer, BodyStyle и т.д.)")


if __name__ == "__main__":
    print("="*80)
    print("ПОИСК С ИСПОЛЬЗОВАНИЕМ KNOWLEDGE GRAPH EMBEDDINGS")
    print("="*80)
    
    # Загружаем онтологию
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://cars_ontology.owl").load()
    print(f"   ✓ Загружено автомобилей: {len(list(onto.Vehicle.instances()))}")
    
    # Загружаем KG embeddings
    try:
        model, entity_to_id, relation_to_id, id_to_entity, id_to_relation = load_kg_embeddings()
    except FileNotFoundError as e:
        print(f"   ❌ Ошибка: {e}")
        print("   💡 Запустите сначала: python create_kg_embeddings.py")
        exit(1)
    
    # Пример 1: Поиск автомобилей по производителю
    print("\n" + "="*80)
    print("ПРИМЕР 1: Найти все автомобили от BMW")
    print("="*80)
    print("\n📝 Запрос: (?, MadeBy, BMW)")
    print("   Ищем все автомобили, которые сделаны BMW")
    print("   ⚠️  ВАЖНО: Используем direction='backward' для поиска (?, relation, entity)")
    
    # Нужно найти правильное имя BMW в индексе
    bmw_name = None
    for entity_name in entity_to_id.keys():
        if 'BMW' in entity_name.upper() and entity_name.startswith('BMW') and 'BMW' == entity_name:
            bmw_name = entity_name
            break
    
    # Если не нашли точное совпадение, ищем любое BMW
    if not bmw_name:
        for entity_name in entity_to_id.keys():
            if entity_name.upper() == 'BMW':
                bmw_name = entity_name
                break
    
    if bmw_name:
        results = find_vehicles_by_relation(
            bmw_name, 'MadeBy', model, entity_to_id, relation_to_id, id_to_entity, 
            top_k=10, direction="backward"  # ВАЖНО: backward для (?, MadeBy, BMW)
        )
        display_kg_results(results, onto, query_type="relation", entity_name=bmw_name, relation_name="MadeBy")
    else:
        print("❌ BMW не найден в индексе")
        print("   Доступные производители (первые 10):")
        manufacturers = [e for e in entity_to_id.keys() if len(e.split('_')) == 1][:10]
        for m in manufacturers:
            print(f"   - {m}")
    
    # Пример 2: Поиск похожих сущностей
    if len(entity_to_id) > 0:
        print("\n" + "="*80)
        print("ПРИМЕР 2: Найти похожие сущности")
        print("="*80)
        
        # Берем первый Vehicle из индекса
        vehicle_name = None
        for entity_name in entity_to_id.keys():
            # Ищем Vehicle (обычно содержат год и ID)
            if any(char.isdigit() for char in entity_name) and len(entity_name.split('_')) >= 3:
                vehicle_name = entity_name
                break
        
        if vehicle_name:
            print(f"\n📝 Запрос: Найти похожие на {clean_name_for_display(vehicle_name)}")
            similar = find_similar_entities_by_embedding(
                vehicle_name, model, entity_to_id, id_to_entity, top_k=5
            )
            display_kg_results(similar, onto, query_type="similarity")
    
    print("\n" + "="*80)
    print("ПОИСК ЗАВЕРШЕН")
    print("="*80)
    print("\n💡 Как использовать:")
    print("   1. find_vehicles_by_relation(entity, relation, ...) - поиск по связи")
    print("   2. find_similar_entities_by_embedding(entity, ...) - поиск похожих")
    print("   3. Используйте предсказание связей для link prediction")

