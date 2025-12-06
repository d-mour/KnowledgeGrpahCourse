#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
БЫСТРАЯ ВАЛИДАЦИЯ Knowledge Graph Embeddings

Проверяет на конкретных примерах, что модель предсказывает правильные связи.
"""

from owlready2 import *
import os
import json

try:
    from pykeen.models import TransE
    from pykeen.triples import TriplesFactory
    import torch
    HAS_PYKEEN = True
except ImportError:
    HAS_PYKEEN = False
    print("❌ PyKEEN не установлен")

def load_model_simple(model_dir: str = "kg_embeddings_pykeen"):
    """Загружает модель"""
    model_path = os.path.join(model_dir, "trained_model.pkl")
    model = torch.load(model_path, map_location='cpu', weights_only=False)
    
    with open(os.path.join(model_dir, "entity_to_id.json"), 'r') as f:
        entity_to_id = json.load(f)
    with open(os.path.join(model_dir, "relation_to_id.json"), 'r') as f:
        relation_to_id = json.load(f)
    
    id_to_entity = {v: k for k, v in entity_to_id.items()}
    
    return model, entity_to_id, relation_to_id, id_to_entity


def predict_tail(model, head_id, relation_id, top_k=10):
    """Предсказание tail для (head, relation, ?)"""
    num_entities = model.num_entities
    hrt_batch = torch.zeros((num_entities, 3), dtype=torch.long)
    hrt_batch[:, 0] = head_id
    hrt_batch[:, 1] = relation_id
    hrt_batch[:, 2] = torch.arange(num_entities)
    
    with torch.no_grad():
        scores = model.score_hrt(hrt_batch).squeeze(-1)
    
    top_scores, top_indices = torch.topk(scores, k=min(top_k, len(scores)))
    return top_indices.tolist(), top_scores.tolist()


def main():
    if not HAS_PYKEEN:
        return
    
    print("="*80)
    print("БЫСТРАЯ ВАЛИДАЦИЯ KNOWLEDGE GRAPH EMBEDDINGS")
    print("="*80)
    
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://" + os.path.abspath("cars_ontology.owl")).load()
    
    print("📂 Загрузка модели...")
    model, entity_to_id, relation_to_id, id_to_entity = load_model_simple()
    print(f"   ✅ Модель загружена: {model.num_entities} сущностей, {model.num_relations} отношений")
    
    print("\n" + "="*80)
    print("ТЕСТ 1: Проверка связи Vehicle -> Manufacturer")
    print("="*80)
    
    test_vehicles = []
    for vehicle in list(onto.Vehicle.instances())[:5]:
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            manufacturer = vehicle.MadeBy[0].name
            test_vehicles.append((vehicle.name, manufacturer))
    
    print(f"\n📋 Проверяем {len(test_vehicles)} автомобилей:")
    
    correct = 0
    for vehicle_name, expected_manufacturer in test_vehicles:
        if vehicle_name not in entity_to_id or 'MadeBy' not in relation_to_id:
            continue
        
        head_id = entity_to_id[vehicle_name]
        relation_id = relation_to_id['MadeBy']
        
        predicted_ids, scores = predict_tail(model, head_id, relation_id, top_k=10)
        predicted_names = [id_to_entity.get(idx, f"?{idx}") for idx in predicted_ids]
        
        is_correct = expected_manufacturer in predicted_names
        if is_correct:
            rank = predicted_names.index(expected_manufacturer) + 1
            status = f"✅ Верно! Ранг: {rank}"
            correct += 1
        else:
            status = "❌ Не в топ-10"
        
        print(f"\n   🚗 {vehicle_name[:40]}...")
        print(f"      Реальный производитель: {expected_manufacturer}")
        print(f"      Топ-3 предсказания: {', '.join(predicted_names[:3])}")
        print(f"      Результат: {status}")
    
    print(f"\n📊 Точность (MadeBy): {correct}/{len(test_vehicles)} ({correct/len(test_vehicles)*100:.0f}%)")
    
    print("\n" + "="*80)
    print("ТЕСТ 2: Проверка связи Vehicle -> BodyStyle")
    print("="*80)
    
    test_styles = []
    for vehicle in list(onto.Vehicle.instances())[:5]:
        if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
            style = vehicle.StyledAs[0].name
            test_styles.append((vehicle.name, style))
    
    print(f"\n📋 Проверяем {len(test_styles)} автомобилей:")
    
    correct_style = 0
    for vehicle_name, expected_style in test_styles:
        if vehicle_name not in entity_to_id or 'StyledAs' not in relation_to_id:
            continue
        
        head_id = entity_to_id[vehicle_name]
        relation_id = relation_to_id['StyledAs']
        
        predicted_ids, scores = predict_tail(model, head_id, relation_id, top_k=10)
        predicted_names = [id_to_entity.get(idx, f"?{idx}") for idx in predicted_ids]
        
        is_correct = expected_style in predicted_names
        if is_correct:
            rank = predicted_names.index(expected_style) + 1
            status = f"✅ Верно! Ранг: {rank}"
            correct_style += 1
        else:
            status = "❌ Не в топ-10"
        
        print(f"\n   🚗 {vehicle_name[:40]}...")
        print(f"      Реальный стиль: {expected_style}")
        print(f"      Топ-3 предсказания: {', '.join(predicted_names[:3])}")
        print(f"      Результат: {status}")
    
    if test_styles:
        print(f"\n📊 Точность (StyledAs): {correct_style}/{len(test_styles)} ({correct_style/len(test_styles)*100:.0f}%)")
    
    print("\n" + "="*80)
    print("ТЕСТ 3: Конкретные известные факты")
    print("="*80)
    
    known_facts = []
    
    for name in entity_to_id.keys():
        if 'BMW' in name and 'Series' in name and '_20' in name:
            known_facts.append((name, 'MadeBy', 'BMW'))
            break
    
    for name in entity_to_id.keys():
        if 'Toyota' in name and 'Camry' in name:
            known_facts.append((name, 'MadeBy', 'Toyota'))
            break
    
    for name in entity_to_id.keys():
        if 'Ford' in name and 'Mustang' in name:
            known_facts.append((name, 'MadeBy', 'Ford'))
            break
    
    print(f"\n📋 Проверяем {len(known_facts)} известных фактов:")
    
    for head_name, relation_name, expected_tail in known_facts:
        if head_name not in entity_to_id or relation_name not in relation_to_id:
            continue
        
        head_id = entity_to_id[head_name]
        relation_id = relation_to_id[relation_name]
        
        predicted_ids, scores = predict_tail(model, head_id, relation_id, top_k=10)
        predicted_names = [id_to_entity.get(idx, f"?{idx}") for idx in predicted_ids]
        
        print(f"\n   📝 Факт: ({head_name[:30]}..., {relation_name}, ?)")
        print(f"      Ожидаем: {expected_tail}")
        print(f"      Топ-5 предсказания:")
        
        for i, (pred_name, score) in enumerate(zip(predicted_names[:5], scores[:5]), 1):
            marker = "✅" if pred_name == expected_tail else "  "
            print(f"         {marker} {i}. {pred_name} (score: {score:.4f})")
        
        if expected_tail in predicted_names:
            rank = predicted_names.index(expected_tail) + 1
            print(f"      ✅ ПРАВИЛЬНО! {expected_tail} на позиции {rank}")
        else:
            print(f"      ❌ {expected_tail} не в топ-10")
    
    print("\n" + "="*80)
    print("ИТОГИ")
    print("="*80)
    
    print("""
📌 Как интерпретировать результаты:

1. Score (оценка):
   - В TransE score = -||h + r - t|| (отрицательное расстояние)
   - Чем ВЫШЕ (ближе к 0), тем лучше
   - Score -5.0 лучше, чем -10.0
   
2. Ранг:
   - Ранг 1 = лучший результат (модель уверена)
   - Ранг 2-3 = хороший результат
   - Ранг в топ-10 = приемлемый результат
   
3. Точность:
   - >50% = хорошая модель
   - 20-50% = средняя модель (можно улучшить)
   - <20% = требуется переобучение

4. Что проверяем:
   - Модель должна предсказывать РЕАЛЬНЫЕ связи из онтологии
   - Если BMW_3_Series MadeBy ?, то BMW должен быть в топ результатах
""")


if __name__ == "__main__":
    main()

