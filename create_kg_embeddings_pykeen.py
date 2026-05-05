#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Knowledge Graph Embeddings с использованием PyKEEN

PyKEEN - стандартная библиотека для KGE, упомянутая в лекции.
Использует правильную реализацию TransE и других моделей.
"""

from owlready2 import *
import json
import os
from typing import List, Tuple, Optional

# Загружаем онтологию глобально
onto = get_ontology("file://cars_ontology.owl").load()

try:
    from pykeen.triples import TriplesFactory
    from pykeen.pipeline import pipeline
    from pykeen.models import TransE
    HAS_PYKEEN = True
except ImportError:
    HAS_PYKEEN = False
    print("⚠️  PyKEEN не установлен. Установите: pip install pykeen")


def extract_triples_from_ontology() -> List[Tuple[str, str, str]]:
    """Извлекает триплеты из онтологии"""
    print("="*80)
    print("ИЗВЛЕЧЕНИЕ ТРИПЛЕТОВ ИЗ ГРАФА ЗНАНИЙ")
    print("="*80)
    
    triples = []
    
    # Vehicle --MadeBy--> Manufacturer
    print("\n1. Извлечение связей Vehicle --MadeBy--> Manufacturer...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            for manufacturer in vehicle.MadeBy:
                triples.append((vehicle.name, 'MadeBy', manufacturer.name))
    
    # Vehicle --StyledAs--> BodyStyle
    print("2. Извлечение связей Vehicle --StyledAs--> BodyStyle...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
            for body_style in vehicle.StyledAs:
                triples.append((vehicle.name, 'StyledAs', body_style.name))
    
    # Vehicle --hasSegment--> MarketSegment
    print("3. Извлечение связей Vehicle --hasSegment--> MarketSegment...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'hasSegment') and vehicle.hasSegment:
            for segment in vehicle.hasSegment:
                triples.append((vehicle.name, 'hasSegment', segment.name))
    
    # Vehicle --hasEngine--> Engine
    print("4. Извлечение связей Vehicle --hasEngine--> Engine...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'hasEngine') and vehicle.hasEngine:
            for engine in vehicle.hasEngine:
                triples.append((vehicle.name, 'hasEngine', engine.name))
    
    # Vehicle --hasTransmission--> Transmission
    print("5. Извлечение связей Vehicle --hasTransmission--> Transmission...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'hasTransmission') and vehicle.hasTransmission:
            for transmission in vehicle.hasTransmission:
                triples.append((vehicle.name, 'hasTransmission', transmission.name))
    
    # Manufacturer --WhereIs--> Country
    print("6. Извлечение связей Manufacturer --WhereIs--> Country...")
    for manufacturer in onto.Manufacturer.instances():
        if hasattr(manufacturer, 'WhereIs') and manufacturer.WhereIs:
            for country in manufacturer.WhereIs:
                triples.append((manufacturer.name, 'WhereIs', country.name))
    
    print(f"\n✅ Извлечено триплетов: {len(triples)}")
    
    return triples


def create_kg_embeddings_pykeen(limit: Optional[int] = None,
                                embedding_dim: int = 64,
                                num_epochs: int = 100,
                                model_name: str = "TransE"):
    """
    СОЗДАНИЕ KNOWLEDGE GRAPH EMBEDDINGS С ИСПОЛЬЗОВАНИЕМ PyKEEN
    
    PyKEEN - стандартная библиотека, упомянутая в лекции.
    Использует правильную реализацию моделей KGE.
    """
    if not HAS_PYKEEN:
        print("\n❌ PyKEEN не установлен!")
        print("   Установите: pip install pykeen")
        return None
    
    print("="*80)
    print("СОЗДАНИЕ KNOWLEDGE GRAPH EMBEDDINGS (PyKEEN)")
    print("="*80)
    
    # Извлекаем триплеты
    triples = extract_triples_from_ontology()
    
    if limit:
        triples = triples[:limit]
        print(f"\n⚠️  Ограничение: используем первые {limit} триплетов")
    
    if len(triples) == 0:
        print("❌ Триплеты не найдены!")
        return None
    
    # Сохраняем триплеты во временный файл для PyKEEN
    temp_file = "temp_triples.tsv"
    with open(temp_file, 'w', encoding='utf-8') as f:
        for h, r, t in triples:
            f.write(f"{h}\t{r}\t{t}\n")
    
    print(f"\n✅ Триплеты сохранены в {temp_file}")
    
    # Создаем TriplesFactory из файла
    print("\n📂 Загрузка триплетов в PyKEEN...")
    triples_factory = TriplesFactory.from_path(temp_file)
    
    print(f"   Сущностей: {triples_factory.num_entities}")
    print(f"   Отношений: {triples_factory.num_relations}")
    print(f"   Триплетов: {triples_factory.num_triples}")
    
    # Разделяем на train/test (80/20)
    training, testing = triples_factory.split([0.8, 0.2])
    
    print(f"\n📊 Разделение данных:")
    print(f"   Train: {training.num_triples} триплетов")
    print(f"   Test: {testing.num_triples} триплетов")
    
    # Создаем pipeline для обучения
    print(f"\n🚀 Запуск обучения модели {model_name}...")
    print(f"   Эпох: {num_epochs}")
    print(f"   Размерность embeddings: {embedding_dim}")
    
    result = pipeline(
        training=training,
        testing=testing,
        model=model_name,
        model_kwargs=dict(embedding_dim=embedding_dim),
        training_kwargs=dict(num_epochs=num_epochs),
        random_seed=42,
        device='cpu',  # Используем CPU (можно 'cuda' если есть GPU)
    )
    
    print(f"\n✅ Обучение завершено!")
    
    # Сохраняем результаты
    output_dir = "kg_embeddings_pykeen"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем модель
    result.save_to_directory(output_dir)
    
    print(f"\n✅ Модель сохранена в: {output_dir}/")
    
    # Выводим метрики
    print(f"\n📊 Метрики качества:")
    try:
        # PyKEEN хранит метрики в metric_results
        if hasattr(result, 'metric_results'):
            metrics = result.metric_results.to_dict()
            if 'both' in metrics and 'realistic' in metrics['both']:
                realistic = metrics['both']['realistic']
                mr = realistic.get('arithmetic_mean_rank', 'N/A')
                mrr = realistic.get('inverse_harmonic_mean_rank', 'N/A')
                hits10 = realistic.get('hits_at_10', 'N/A')
                print(f"   MR (Mean Rank): {mr}")
                print(f"   MRR: {mrr}")
                print(f"   Hits@10: {hits10}")
            else:
                print(f"   Метрики доступны в result.metric_results")
        else:
            print(f"   Метрики будут сохранены в results.json")
    except Exception as e:
        print(f"   ⚠️  Не удалось получить метрики: {e}")
        print(f"   Метрики сохранены в {output_dir}/results.json")
    
    # Сохраняем маппинги
    # PyKEEN использует свои индексы, нужно сохранить их
    entity_to_id = {}
    relation_to_id = {}
    
    # Получаем маппинги из triples_factory
    for idx, entity in enumerate(triples_factory.entity_to_id.keys()):
        entity_to_id[entity] = idx
    
    for idx, rel in enumerate(triples_factory.relation_to_id.keys()):
        relation_to_id[rel] = idx
    
    with open(os.path.join(output_dir, "entity_to_id.json"), 'w', encoding='utf-8') as f:
        json.dump(entity_to_id, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "relation_to_id.json"), 'w', encoding='utf-8') as f:
        json.dump(relation_to_id, f, ensure_ascii=False, indent=2)
    
    # Также сохраняем triples_factory для удобства
    try:
        training.save(os.path.join(output_dir, "training_triples"))
    except:
        # Если метод save не работает, сохраняем вручную
        pass
    
    # Удаляем временный файл
    if os.path.exists(temp_file):
        os.remove(temp_file)
    
    print(f"\n✅ Все готово! Используйте:")
    print(f"   from pykeen.models import TransE")
    print(f"   model = TransE.from_pretrained('{output_dir}')")
    
    return result


if __name__ == "__main__":
    import sys
    
    limit = None
    embedding_dim = 64
    num_epochs = 100
    model_name = "TransE"
    
    if len(sys.argv) > 1:
        if '--limit' in sys.argv:
            limit_idx = sys.argv.index('--limit')
            if limit_idx + 1 < len(sys.argv):
                limit = int(sys.argv[limit_idx + 1])
        
        if '--dim' in sys.argv:
            dim_idx = sys.argv.index('--dim')
            if dim_idx + 1 < len(sys.argv):
                embedding_dim = int(sys.argv[dim_idx + 1])
        
        if '--epochs' in sys.argv:
            epochs_idx = sys.argv.index('--epochs')
            if epochs_idx + 1 < len(sys.argv):
                num_epochs = int(sys.argv[epochs_idx + 1])
        
        if '--model' in sys.argv:
            model_idx = sys.argv.index('--model')
            if model_idx + 1 < len(sys.argv):
                model_name = sys.argv[model_idx + 1]
    
    create_kg_embeddings_pykeen(
        limit=limit,
        embedding_dim=embedding_dim,
        num_epochs=num_epochs,
        model_name=model_name
    )

