#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестирование качества Knowledge Graph Embeddings

Проверяет:
1. Правильность загрузки embeddings
2. Качество предсказаний (score правильных vs неправильных связей)
3. Примеры поиска
"""

from owlready2 import *
from search_with_kg_embeddings import load_kg_embeddings, find_vehicles_by_relation, find_similar_entities_by_embedding
from sparql_queries import clean_name_for_display
import numpy as np


def test_loading():
    """Проверка загрузки embeddings"""
    print("="*80)
    print("ТЕСТ 1: Загрузка embeddings")
    print("="*80)
    
    try:
        model, entity_to_id, relation_to_id, id_to_entity, id_to_relation = load_kg_embeddings()
        print("✅ Embeddings загружены успешно")
        print(f"   Сущностей: {len(entity_to_id)}")
        print(f"   Отношений: {len(relation_to_id)}")
        print(f"   Размерность: {model.embedding_dim}")
        return model, entity_to_id, relation_to_id, id_to_entity, id_to_relation
    except Exception as e:
        print(f"❌ Ошибка загрузки: {e}")
        return None


def test_score_quality(model, entity_to_id, relation_to_id, id_to_entity, onto):
    """Проверка качества score на известных связях"""
    print("\n" + "="*80)
    print("ТЕСТ 2: Качество предсказаний")
    print("="*80)
    
    # Берем несколько известных связей из онтологии
    test_cases = []
    vehicles = list(onto.Vehicle.instances())[:10]  # Первые 10 для теста
    
    for vehicle in vehicles:
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            manufacturer = vehicle.MadeBy[0]
            if vehicle.name in entity_to_id and manufacturer.name in entity_to_id:
                test_cases.append((vehicle.name, 'MadeBy', manufacturer.name, True))
    
    if not test_cases:
        print("❌ Не найдено тестовых случаев")
        return
    
    print(f"\n📊 Тестируем {len(test_cases)} известных связей...")
    
    correct_scores = []
    incorrect_scores = []
    
    # Создаем множество всех правильных связей для проверки
    correct_triples_set = set()
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            manufacturer = vehicle.MadeBy[0]
            if vehicle.name in entity_to_id and manufacturer.name in entity_to_id:
                v_id = entity_to_id[vehicle.name]
                m_id = entity_to_id[manufacturer.name]
                r_id = relation_to_id['MadeBy']
                correct_triples_set.add((v_id, r_id, m_id))
    
    for vehicle_name, relation, manufacturer_name, is_correct in test_cases:
        vehicle_id = entity_to_id[vehicle_name]
        manufacturer_id = entity_to_id[manufacturer_name]
        relation_id = relation_to_id[relation]
        
        # Score правильной связи (vehicle, MadeBy, manufacturer)
        correct_score = model.score(vehicle_id, relation_id, manufacturer_id)
        correct_scores.append(correct_score)
        
        # Score неправильной связи - берем производителя, который точно не связан с этим автомобилем
        # Пробуем несколько случайных производителей, пока не найдем неправильный
        import random
        wrong_manufacturer_id = None
        attempts = 0
        while wrong_manufacturer_id is None and attempts < 100:
            candidate_id = random.randint(0, len(entity_to_id) - 1)
            # Проверяем, что это не правильная связь
            if (vehicle_id, relation_id, candidate_id) not in correct_triples_set:
                # Также проверяем, что это действительно производитель (не Vehicle)
                candidate_name = id_to_entity[candidate_id]
                # Производители обычно короткие имена без цифр
                if len(candidate_name.split('_')) == 1 and not any(c.isdigit() for c in candidate_name):
                    wrong_manufacturer_id = candidate_id
            attempts += 1
        
        if wrong_manufacturer_id is None:
            # Если не нашли подходящего, берем просто другой ID
            wrong_manufacturer_id = (manufacturer_id + 100) % len(entity_to_id)
        
        wrong_score = model.score(vehicle_id, relation_id, wrong_manufacturer_id)
        incorrect_scores.append(wrong_score)
    
    avg_correct = np.mean(correct_scores)
    avg_incorrect = np.mean(incorrect_scores)
    
    print(f"\n✅ Результаты:")
    print(f"   Средний score ПРАВИЛЬНЫХ связей: {avg_correct:.4f}")
    print(f"   Средний score НЕПРАВИЛЬНЫХ связей: {avg_incorrect:.4f}")
    print(f"   Разница: {abs(avg_correct - avg_incorrect):.4f}")
    
    # В TransE правильные связи должны иметь БОЛЬШИЙ score (ближе к 0)
    # Score = -||h + r - t||, поэтому правильные должны быть ближе к 0
    if avg_correct > avg_incorrect:
        print(f"   ✅ Модель правильно различает связи!")
        if avg_correct > -5.0:
            print(f"   🎯 Отличное качество (score правильных > -5.0)")
        elif avg_correct > -10.0:
            print(f"   👍 Хорошее качество (score правильных > -10.0)")
        else:
            print(f"   ⚠️  Среднее качество (score правильных < -10.0)")
    else:
        print(f"   ❌ Модель не различает связи!")
        print(f"   ⚠️  Проблема: правильные связи имеют ХУДШИЙ score чем неправильные")
        print(f"   💡 Возможные причины:")
        print(f"      1. Модель плохо обучена (loss растет вместо уменьшения)")
        print(f"      2. Learning rate слишком большой или маленький")
        print(f"      3. Недостаточно эпох обучения")
        print(f"   💡 Решение: переобучите с другими параметрами:")
        print(f"      python create_kg_embeddings.py --epochs 200 --dim 64")


def test_search_examples(model, entity_to_id, relation_to_id, id_to_entity, onto):
    """Тестирование примеров поиска"""
    print("\n" + "="*80)
    print("ТЕСТ 3: Примеры поиска")
    print("="*80)
    
    # Ищем производителей в индексе
    manufacturers = [e for e in entity_to_id.keys() if len(e.split('_')) == 1][:5]
    
    if not manufacturers:
        print("❌ Производители не найдены в индексе")
        return
    
    print(f"\n📋 Тестируем поиск для производителей: {', '.join(manufacturers[:3])}")
    
    for manufacturer in manufacturers[:3]:
        print(f"\n{'─'*80}")
        print(f"Поиск автомобилей от {manufacturer}")
        print(f"{'─'*80}")
        
        results = find_vehicles_by_relation(
            manufacturer, 'MadeBy', model, entity_to_id, relation_to_id, id_to_entity,
            top_k=5, direction="backward"
        )
        
        if results:
            print(f"\n✅ Найдено {len(results)} результатов:")
            for idx, (vehicle_name, score) in enumerate(results[:3], 1):
                print(f"   {idx}. {clean_name_for_display(vehicle_name)} (score: {score:.4f})")
                
                # Проверяем, действительно ли это правильный производитель
                vehicle = None
                for v in onto.Vehicle.instances():
                    if v.name == vehicle_name:
                        vehicle = v
                        break
                
                if vehicle and hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
                    actual_manufacturer = vehicle.MadeBy[0].name
                    if actual_manufacturer == manufacturer:
                        print(f"      ✅ Правильно! Производитель: {actual_manufacturer}")
                    else:
                        print(f"      ❌ Неправильно! Ожидалось: {manufacturer}, получено: {actual_manufacturer}")
        else:
            print(f"   ❌ Результаты не найдены")


def test_similarity_search(model, entity_to_id, id_to_entity, onto):
    """Тестирование поиска похожих сущностей"""
    print("\n" + "="*80)
    print("ТЕСТ 4: Поиск похожих сущностей")
    print("="*80)
    
    # Берем первый Vehicle из индекса
    vehicle_name = None
    for entity_name in entity_to_id.keys():
        if any(char.isdigit() for char in entity_name) and len(entity_name.split('_')) >= 3:
            vehicle_name = entity_name
            break
    
    if not vehicle_name:
        print("❌ Vehicle не найден для теста")
        return
    
    print(f"\n📋 Ищем похожие на: {clean_name_for_display(vehicle_name)}")
    
    similar = find_similar_entities_by_embedding(vehicle_name, model, entity_to_id, id_to_entity, top_k=5)
    
    if similar:
        print(f"\n✅ Найдено {len(similar)} похожих сущностей:")
        for idx, (similar_name, similarity) in enumerate(similar, 1):
            print(f"   {idx}. {clean_name_for_display(similar_name)} (сходство: {similarity:.4f})")
    else:
        print("   ❌ Похожие сущности не найдены")


def main():
    """Главная функция тестирования"""
    print("="*80)
    print("ТЕСТИРОВАНИЕ KNOWLEDGE GRAPH EMBEDDINGS")
    print("="*80)
    
    # Загружаем онтологию
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://cars_ontology.owl").load()
    print(f"   ✓ Загружено автомобилей: {len(list(onto.Vehicle.instances()))}")
    
    # Тест 1: Загрузка
    result = test_loading()
    if not result:
        print("\n❌ Не удалось загрузить embeddings. Запустите сначала:")
        print("   python create_kg_embeddings.py --epochs 150 --dim 64")
        return
    
    model, entity_to_id, relation_to_id, id_to_entity, id_to_relation = result
    
    # Тест 2: Качество
    test_score_quality(model, entity_to_id, relation_to_id, id_to_entity, onto)
    
    # Тест 3: Примеры поиска
    test_search_examples(model, entity_to_id, relation_to_id, id_to_entity, onto)
    
    # Тест 4: Поиск похожих
    test_similarity_search(model, entity_to_id, id_to_entity, onto)
    
    print("\n" + "="*80)
    print("ТЕСТИРОВАНИЕ ЗАВЕРШЕНО")
    print("="*80)
    print("\n💡 Если результаты хорошие, можете использовать:")
    print("   python search_with_kg_embeddings.py")
    print("\n💡 Если результаты плохие, переобучите модель:")
    print("   python create_kg_embeddings.py --epochs 200 --dim 64")


if __name__ == "__main__":
    main()

