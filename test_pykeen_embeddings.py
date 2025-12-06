#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Тестирование и демонстрация Knowledge Graph Embeddings (PyKEEN)

Показывает правильную работу обученной модели:
1. Загрузка модели
2. Предсказание связей (link prediction)
3. Поиск похожих сущностей
4. Примеры использования
"""

from owlready2 import *
import os
from sparql_queries import clean_name_for_display

try:
    from pykeen.models import TransE
    from pykeen.triples import TriplesFactory
    import torch
    HAS_PYKEEN = True
except ImportError:
    HAS_PYKEEN = False
    print("❌ PyKEEN не установлен. Установите: pip install pykeen")


def load_pykeen_model(model_dir: str = "kg_embeddings_pykeen"):
    """Загружает обученную модель PyKEEN"""
    if not HAS_PYKEEN:
        return None
    
    print("="*80)
    print("ЗАГРУЗКА МОДЕЛИ PyKEEN")
    print("="*80)
    
    try:
        # Способ 1: Через load_model (если доступен)
        try:
            from pykeen import load_model
            model = load_model(model_dir)
            
            # Загружаем triples_factory
            triples_factory_path = os.path.join(model_dir, "training_triples")
            if os.path.exists(triples_factory_path):
                triples_factory = TriplesFactory.load(triples_factory_path)
            else:
                triples_factory = None
            
            print(f"✅ Модель загружена из {model_dir}")
            print(f"   Размерность embeddings: {model.embedding_dim}")
            print(f"   Сущностей: {model.num_entities}")
            print(f"   Отношений: {model.num_relations}")
            
            return model, triples_factory
        except ImportError:
            pass
        
        # Способ 2: Загружаем через файлы напрямую
        # Читаем metadata для получения информации о модели
        metadata_path = os.path.join(model_dir, "metadata.json")
        import json
        try:
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        except:
            metadata = {}
        
        model_name = metadata.get('model', {}).get('model', 'TransE') if metadata else 'TransE'
        model_kwargs = metadata.get('model', {}).get('model_kwargs', {}) if metadata else {'embedding_dim': 64}
        
        # Загружаем triples_factory из сохраненных файлов
        triples_factory_path = os.path.join(model_dir, "training_triples")
        if os.path.exists(triples_factory_path):
            # PyKEEN сохраняет triples_factory в бинарном формате
            try:
                triples_factory = TriplesFactory.from_path_binary(triples_factory_path)
            except:
                # Если не работает, создаем из TSV файлов
                numeric_triples_path = os.path.join(triples_factory_path, "numeric_triples.tsv.gz")
                entity_to_id_path = os.path.join(triples_factory_path, "entity_to_id.tsv.gz")
                relation_to_id_path = os.path.join(triples_factory_path, "relation_to_id.tsv.gz")
                
                if all(os.path.exists(p) for p in [numeric_triples_path, entity_to_id_path, relation_to_id_path]):
                    triples_factory = TriplesFactory.from_path(
                        path=numeric_triples_path,
                        entity_to_id_path=entity_to_id_path,
                        relation_to_id_path=relation_to_id_path
                    )
                else:
                    triples_factory = None
        else:
            triples_factory = None
        
        # Создаем модель с теми же параметрами
        if model_name == "TransE":
            from pykeen.models import TransE
            if triples_factory:
                model = TransE(
                    triples_factory=triples_factory,
                    **model_kwargs
                )
            else:
                # Если triples_factory нет, создаем модель с известными параметрами
                num_entities = model_kwargs.get('num_entities', 13379)
                num_relations = model_kwargs.get('num_relations', 6)
                embedding_dim = model_kwargs.get('embedding_dim', 64)
                model = TransE(
                    num_entities=num_entities,
                    num_relations=num_relations,
                    embedding_dim=embedding_dim
                )
        else:
            print(f"⚠️  Модель {model_name} - используем TransE по умолчанию")
            from pykeen.models import TransE
            if triples_factory:
                model = TransE(triples_factory=triples_factory, embedding_dim=64)
            else:
                model = TransE(num_entities=13379, num_relations=6, embedding_dim=64)
        
        # Загружаем веса модели
        model_path = os.path.join(model_dir, "trained_model.pkl")
        if os.path.exists(model_path):
            try:
                import torch
                # Загружаем с weights_only=False (PyKEEN использует сложные объекты)
                loaded = torch.load(model_path, map_location='cpu', weights_only=False)
                
                if isinstance(loaded, dict):
                    if 'state_dict' in loaded:
                        model.load_state_dict(loaded['state_dict'])
                    else:
                        model.load_state_dict(loaded)
                elif hasattr(loaded, 'load_state_dict'):
                    # Это полная модель
                    model = loaded
                else:
                    model.load_state_dict(loaded)
            except Exception as e:
                print(f"   ⚠️  Не удалось загрузить веса модели: {e}")
        
        print(f"✅ Модель загружена из {model_dir}")
        
        # Получаем атрибуты модели (в PyKEEN они могут быть в разных местах)
        embedding_dim = getattr(model, 'embedding_dim', None) or getattr(model, '_embedding_dim', None) or model_kwargs.get('embedding_dim', 64)
        num_entities = getattr(model, 'num_entities', None) or (triples_factory.num_entities if triples_factory else 13379)
        num_relations = getattr(model, 'num_relations', None) or (triples_factory.num_relations if triples_factory else 6)
        
        print(f"   Размерность embeddings: {embedding_dim}")
        print(f"   Сущностей: {num_entities}")
        print(f"   Отношений: {num_relations}")
        
        return model, triples_factory
        
    except Exception as e:
        print(f"❌ Ошибка загрузки модели: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def load_entity_mappings(mapping_dir: str = "kg_embeddings_pykeen"):
    """Загружает маппинги сущностей и отношений"""
    import json
    
    entity_to_id = {}
    relation_to_id = {}
    id_to_entity = {}
    id_to_relation = {}
    
    try:
        # Пробуем загрузить из сохраненного triples_factory
        triples_factory_path = os.path.join(mapping_dir, "training_triples")
        if os.path.exists(triples_factory_path):
            try:
                triples_factory = TriplesFactory.load(triples_factory_path)
                # Получаем маппинги из triples_factory
                for idx, entity in enumerate(triples_factory.entity_to_id.keys()):
                    entity_to_id[entity] = idx
                for idx, rel in enumerate(triples_factory.relation_to_id.keys()):
                    relation_to_id[rel] = idx
            except:
                pass
        
        # Если не загрузилось, пробуем из JSON
        if not entity_to_id:
            entity_file = os.path.join(mapping_dir, "entity_to_id.json")
            relation_file = os.path.join(mapping_dir, "relation_to_id.json")
            
            if os.path.exists(entity_file):
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity_to_id = json.load(f)
            
            if os.path.exists(relation_file):
                with open(relation_file, 'r', encoding='utf-8') as f:
                    relation_to_id = json.load(f)
        
        # Создаем обратные маппинги
        id_to_entity = {v: k for k, v in entity_to_id.items()}
        id_to_relation = {v: k for k, v in relation_to_id.items()}
        
        if entity_to_id:
            print(f"✅ Маппинги загружены:")
            print(f"   Сущностей: {len(entity_to_id)}")
            print(f"   Отношений: {len(relation_to_id)}")
        else:
            print(f"⚠️  Маппинги не найдены, используем модель напрямую")
        
        return entity_to_id, relation_to_id, id_to_entity, id_to_relation
    except Exception as e:
        print(f"⚠️  Ошибка загрузки маппингов: {e}")
        return {}, {}, {}, {}


def predict_tail(model, head_name: str, relation_name: str,
                entity_to_id: dict, relation_to_id: dict, id_to_entity: dict,
                top_k: int = 10):
    """
    ПРЕДСКАЗАНИЕ TAIL для (head, relation, ?)
    
    Пример: (BMW_3_Series_2016, MadeBy, ?) → предсказывает производителя
    """
    if head_name not in entity_to_id or relation_name not in relation_to_id:
        print(f"❌ Сущность или отношение не найдено")
        return []
    
    head_id = entity_to_id[head_name]
    relation_id = relation_to_id[relation_name]
    
    print(f"\n🔍 Предсказание: ({head_name}, {relation_name}, ?)")
    print(f"   Head ID: {head_id}, Relation ID: {relation_id}")
    
    num_entities = model.num_entities
    
    hrt_batch = torch.zeros((num_entities, 3), dtype=torch.long)
    hrt_batch[:, 0] = head_id
    hrt_batch[:, 1] = relation_id
    hrt_batch[:, 2] = torch.arange(num_entities)
    
    with torch.no_grad():
        scores = model.score_hrt(hrt_batch)
    
    scores = scores.squeeze(-1)
    
    top_scores, top_indices = torch.topk(scores, k=min(top_k, len(scores)))
    tail_ids = top_indices.tolist()
    scores_list = top_scores.tolist()
    
    results = []
    for tail_id, score in zip(tail_ids, scores_list):
        tail_name = id_to_entity.get(int(tail_id), f"Entity_{int(tail_id)}")
        results.append((tail_name, float(score)))
    
    return results


def predict_head(model, relation_name: str, tail_name: str,
                entity_to_id: dict, relation_to_id: dict, id_to_entity: dict,
                top_k: int = 10):
    """
    ПРЕДСКАЗАНИЕ HEAD для (?, relation, tail)
    
    Пример: (?, MadeBy, BMW) → предсказывает все автомобили от BMW
    """
    if tail_name not in entity_to_id or relation_name not in relation_to_id:
        print(f"❌ Сущность или отношение не найдено")
        return []
    
    tail_id = entity_to_id[tail_name]
    relation_id = relation_to_id[relation_name]
    
    print(f"\n🔍 Предсказание: (?, {relation_name}, {tail_name})")
    print(f"   Tail ID: {tail_id}, Relation ID: {relation_id}")
    
    num_entities = model.num_entities
    
    hrt_batch = torch.zeros((num_entities, 3), dtype=torch.long)
    hrt_batch[:, 0] = torch.arange(num_entities)
    hrt_batch[:, 1] = relation_id
    hrt_batch[:, 2] = tail_id
    
    with torch.no_grad():
        scores = model.score_hrt(hrt_batch)
    
    scores = scores.squeeze(-1)
    
    top_scores, top_indices = torch.topk(scores, k=min(top_k, len(scores)))
    head_ids = top_indices.tolist()
    scores_list = top_scores.tolist()
    
    results = []
    for head_id, score in zip(head_ids, scores_list):
        head_name_result = id_to_entity.get(int(head_id), f"Entity_{int(head_id)}")
        results.append((head_name_result, float(score)))
    
    return results


def find_similar_entities(model, entity_name: str, entity_to_id: dict, id_to_entity: dict, top_k: int = 10):
    """Находит похожие сущности по embedding"""
    if entity_name not in entity_to_id:
        return []
    
    entity_id = entity_to_id[entity_name]
    
    with torch.no_grad():
        all_entity_ids = torch.arange(model.num_entities, dtype=torch.long)
        all_embeddings = model.entity_representations[0](all_entity_ids)
        
        entity_embedding = all_embeddings[entity_id]
        
        similarities = torch.nn.functional.cosine_similarity(
            entity_embedding.unsqueeze(0), all_embeddings, dim=1
        )
    
    top_scores, top_indices = torch.topk(similarities, k=min(top_k + 1, len(similarities)), dim=-1)
    
    results = []
    for score, idx in zip(top_scores, top_indices):
        idx_val = int(idx.item())
        if idx_val != entity_id:
            similar_name = id_to_entity.get(idx_val, f"Entity_{idx_val}")
            results.append((similar_name, float(score.item())))
            if len(results) >= top_k:
                break
    
    return results


def display_results(results, onto, query_type: str = "prediction"):
    """Выводит результаты с информацией об автомобилях"""
    print("\n" + "="*80)
    print(f"РЕЗУЛЬТАТЫ: найдено {len(results)} сущностей")
    print("="*80)
    
    for idx, (entity_name, score) in enumerate(results, 1):
        print(f"\n{idx}. {clean_name_for_display(entity_name)}")
        print(f"   Score: {score:.4f}")
        
        # Пытаемся найти в онтологии
        vehicle = None
        for v in onto.Vehicle.instances():
            if v.name == entity_name:
                vehicle = v
                break
        
        if vehicle:
            print(f"   📋 Информация:")
            if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
                print(f"      Производитель: {clean_name_for_display(vehicle.MadeBy[0].name)}")
            if hasattr(vehicle, 'Year') and vehicle.Year:
                print(f"      Год: {vehicle.Year}")
            if hasattr(vehicle, 'MSRP') and vehicle.MSRP:
                print(f"      Цена: ${vehicle.MSRP:,.0f}")


def demonstrate_link_prediction(model, entity_to_id, relation_to_id, id_to_entity, onto):
    """Демонстрация предсказания связей"""
    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ 1: Предсказание связей (Link Prediction)")
    print("="*80)
    
    # Пример 1: Найти производителя автомобиля
    print("\n📝 Пример 1: Кто производит этот автомобиль?")
    print("   Запрос: (BMW_3_Series_2016_145, MadeBy, ?)")
    
    # Ищем Vehicle в индексе
    vehicle_name = None
    for name in entity_to_id.keys():
        if 'BMW' in name and '3_Series' in name and '2016' in name:
            vehicle_name = name
            break
    
    if vehicle_name:
        results = predict_tail(model, vehicle_name, 'MadeBy', 
                             entity_to_id, relation_to_id, id_to_entity, top_k=5)
        display_results(results, onto)
    else:
        print("   ⚠️  BMW 3 Series 2016 не найден, используем первый Vehicle")
        vehicle_name = list(entity_to_id.keys())[0]
        if 'MadeBy' in relation_to_id:
            results = predict_tail(model, vehicle_name, 'MadeBy',
                                 entity_to_id, relation_to_id, id_to_entity, top_k=5)
            display_results(results, onto)
    
    # Пример 2: Найти все автомобили от производителя
    print("\n" + "="*80)
    print("📝 Пример 2: Какие автомобили производит BMW?")
    print("   Запрос: (?, MadeBy, BMW)")
    
    bmw_name = None
    for name in entity_to_id.keys():
        if name.upper() == 'BMW':
            bmw_name = name
            break
    
    if bmw_name and 'MadeBy' in relation_to_id:
        results = predict_head(model, 'MadeBy', bmw_name,
                             entity_to_id, relation_to_id, id_to_entity, top_k=10)
        display_results(results, onto)
    else:
        print("   ⚠️  BMW не найден в индексе")


def demonstrate_similarity_search(model, entity_to_id, id_to_entity, onto):
    """Демонстрация поиска похожих сущностей"""
    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ 2: Поиск похожих сущностей")
    print("="*80)
    
    # Ищем Vehicle в индексе
    vehicle_name = None
    for name in entity_to_id.keys():
        if any(char.isdigit() for char in name) and len(name.split('_')) >= 3:
            vehicle_name = name
            break
    
    if vehicle_name:
        print(f"\n📝 Ищем похожие на: {clean_name_for_display(vehicle_name)}")
        similar = find_similar_entities(model, vehicle_name, entity_to_id, id_to_entity, top_k=5)
        
        print(f"\n✅ Найдено {len(similar)} похожих сущностей:")
        for idx, (similar_name, similarity) in enumerate(similar, 1):
            print(f"   {idx}. {clean_name_for_display(similar_name)} (сходство: {similarity:.4f})")


def main():
    """Главная функция демонстрации"""
    print("="*80)
    print("ТЕСТИРОВАНИЕ И ДЕМОНСТРАЦИЯ PyKEEN EMBEDDINGS")
    print("="*80)
    
    if not HAS_PYKEEN:
        print("\n❌ PyKEEN не установлен!")
        print("   Установите: pip install pykeen")
        return
    
    # Загружаем онтологию
    print("\n📂 Загрузка онтологии...")
    onto = get_ontology("file://cars_ontology.owl").load()
    print(f"   ✓ Загружено автомобилей: {len(list(onto.Vehicle.instances()))}")
    
    # Загружаем модель
    model, triples_factory = load_pykeen_model()
    if not model:
        print("\n❌ Не удалось загрузить модель")
        print("   Убедитесь, что вы запустили: python create_kg_embeddings_pykeen.py")
        return
    
    # Загружаем маппинги
    entity_to_id, relation_to_id, id_to_entity, id_to_relation = load_entity_mappings()
    
    # Если маппинги не загрузились, создаем из triples_factory
    if not entity_to_id and triples_factory:
        print("\n📋 Создание маппингов из triples_factory...")
        entity_to_id = {}
        relation_to_id = {}
        
        for idx, entity in enumerate(triples_factory.entity_to_id.keys()):
            entity_to_id[entity] = idx
        
        for idx, rel in enumerate(triples_factory.relation_to_id.keys()):
            relation_to_id[rel] = idx
        
        id_to_entity = {v: k for k, v in entity_to_id.items()}
        id_to_relation = {v: k for k, v in relation_to_id.items()}
        
        print(f"   ✅ Создано маппингов: {len(entity_to_id)} сущностей, {len(relation_to_id)} отношений")
    
    if not entity_to_id:
        print("\n⚠️  Маппинги не загружены, используем модель напрямую")
        print("   (PyKEEN хранит маппинги внутри модели)")
    
    # Демонстрация 1: Link Prediction
    demonstrate_link_prediction(model, entity_to_id, relation_to_id, id_to_entity, onto)
    
    # Демонстрация 2: Similarity Search
    demonstrate_similarity_search(model, entity_to_id, id_to_entity, onto)
    
    print("\n" + "="*80)
    print("ДЕМОНСТРАЦИЯ ЗАВЕРШЕНА")
    print("="*80)
    print("\n💡 Использование в коде:")
    print("   from pykeen.models import TransE")
    print("   model = TransE.from_pretrained('kg_embeddings_pykeen')")
    print("   scores = model.score_hrt(head_ids, relation_ids, tail_ids)")


if __name__ == "__main__":
    main()

