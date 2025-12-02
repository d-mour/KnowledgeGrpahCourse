#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Knowledge Graph Embeddings (KGE) для графа знаний автомобилей

Реализует подход из лекции:
- Извлекает триплеты (subject, predicate, object) из графа
- Создает embeddings для сущностей (entities) и отношений (relations)
- Обучает модель на задаче link prediction
- Использует модель TransE (простая и эффективная)
"""

from owlready2 import *
import numpy as np
import random
import json
import pickle
import os
from typing import List, Tuple, Dict, Set, Optional
from collections import defaultdict
import math

# Загружаем онтологию
onto = get_ontology("file://cars_ontology.owl").load()

# Базовый namespace
BASE_NS = "http://www.semanticweb.org/fqy/ontologies/2025/9/untitled-ontology-7#"


def extract_triples_from_ontology() -> List[Tuple[str, str, str]]:
    """
    ИЗВЛЕЧЕНИЕ ТРИПЛЕТОВ ИЗ ГРАФА ЗНАНИЙ
    
    Извлекает все триплеты вида (subject, predicate, object) из онтологии.
    Это основа для Knowledge Graph Embeddings.
    
    Триплеты:
    - (Vehicle, MadeBy, Manufacturer)
    - (Vehicle, StyledAs, BodyStyle)
    - (Vehicle, hasSegment, MarketSegment)
    - (Vehicle, hasEngine, Engine)
    - (Manufacturer, WhereIs, Country)
    и т.д.
    
    Returns:
        List[Tuple[str, str, str]]: список триплетов (head, relation, tail)
    """
    print("="*80)
    print("ИЗВЛЕЧЕНИЕ ТРИПЛЕТОВ ИЗ ГРАФА ЗНАНИЙ")
    print("="*80)
    
    triples = []
    
    # 1. Vehicle --MadeBy--> Manufacturer
    print("\n1. Извлечение связей Vehicle --MadeBy--> Manufacturer...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'MadeBy') and vehicle.MadeBy:
            for manufacturer in vehicle.MadeBy:
                triples.append((vehicle.name, 'MadeBy', manufacturer.name))
    
    # 2. Vehicle --StyledAs--> BodyStyle
    print("2. Извлечение связей Vehicle --StyledAs--> BodyStyle...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'StyledAs') and vehicle.StyledAs:
            for body_style in vehicle.StyledAs:
                triples.append((vehicle.name, 'StyledAs', body_style.name))
    
    # 3. Vehicle --hasSegment--> MarketSegment
    print("3. Извлечение связей Vehicle --hasSegment--> MarketSegment...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'hasSegment') and vehicle.hasSegment:
            for segment in vehicle.hasSegment:
                triples.append((vehicle.name, 'hasSegment', segment.name))
    
    # 4. Vehicle --hasEngine--> Engine
    print("4. Извлечение связей Vehicle --hasEngine--> Engine...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'hasEngine') and vehicle.hasEngine:
            for engine in vehicle.hasEngine:
                triples.append((vehicle.name, 'hasEngine', engine.name))
    
    # 5. Vehicle --hasTransmission--> Transmission
    print("5. Извлечение связей Vehicle --hasTransmission--> Transmission...")
    for vehicle in onto.Vehicle.instances():
        if hasattr(vehicle, 'hasTransmission') and vehicle.hasTransmission:
            for transmission in vehicle.hasTransmission:
                triples.append((vehicle.name, 'hasTransmission', transmission.name))
    
    # 6. Manufacturer --WhereIs--> Country
    print("6. Извлечение связей Manufacturer --WhereIs--> Country...")
    for manufacturer in onto.Manufacturer.instances():
        if hasattr(manufacturer, 'WhereIs') and manufacturer.WhereIs:
            for country in manufacturer.WhereIs:
                triples.append((manufacturer.name, 'WhereIs', country.name))
    
    # 7. Engine --MadeBy--> Manufacturer (если есть)
    print("7. Извлечение связей Engine --MadeBy--> Manufacturer...")
    for engine in onto.Engine.instances():
        if hasattr(engine, 'MadeBy') and engine.MadeBy:
            for manufacturer in engine.MadeBy:
                triples.append((engine.name, 'MadeBy', manufacturer.name))
    
    print(f"\n✅ Извлечено триплетов: {len(triples)}")
    
    # Статистика
    relations_count = defaultdict(int)
    for _, rel, _ in triples:
        relations_count[rel] += 1
    
    print(f"\n📊 Статистика по отношениям:")
    for rel, count in sorted(relations_count.items(), key=lambda x: -x[1]):
        print(f"   {rel}: {count}")
    
    return triples


def create_entity_relation_mappings(triples: List[Tuple[str, str, str]]) -> Tuple[Dict[str, int], Dict[str, int], Dict[int, str], Dict[int, str]]:
    """
    СОЗДАНИЕ ИНДЕКСОВ ДЛЯ СУЩНОСТЕЙ И ОТНОШЕНИЙ
    
    Создает маппинги:
    - entity_to_id: имя сущности -> ID
    - relation_to_id: имя отношения -> ID
    - id_to_entity: ID -> имя сущности (обратный)
    - id_to_relation: ID -> имя отношения (обратный)
    
    Это нужно для работы с embeddings (вместо строк используем индексы)
    """
    print("\n" + "="*80)
    print("СОЗДАНИЕ ИНДЕКСОВ ДЛЯ СУЩНОСТЕЙ И ОТНОШЕНИЙ")
    print("="*80)
    
    # Собираем все уникальные сущности и отношения
    entities = set()
    relations = set()
    
    for head, rel, tail in triples:
        entities.add(head)
        entities.add(tail)
        relations.add(rel)
    
    # Создаем маппинги
    entity_list = sorted(list(entities))
    relation_list = sorted(list(relations))
    
    entity_to_id = {entity: idx for idx, entity in enumerate(entity_list)}
    relation_to_id = {rel: idx for idx, rel in enumerate(relation_list)}
    
    id_to_entity = {idx: entity for entity, idx in entity_to_id.items()}
    id_to_relation = {idx: rel for rel, idx in relation_to_id.items()}
    
    print(f"\n✅ Сущностей: {len(entity_to_id)}")
    print(f"✅ Отношений: {len(relation_to_id)}")
    print(f"\n📋 Отношения: {', '.join(relation_list)}")
    
    return entity_to_id, relation_to_id, id_to_entity, id_to_relation


def convert_triples_to_ids(triples: List[Tuple[str, str, str]], 
                          entity_to_id: Dict[str, int],
                          relation_to_id: Dict[str, int]) -> List[Tuple[int, int, int]]:
    """
    КОНВЕРТАЦИЯ ТРИПЛЕТОВ В ИНДЕКСЫ
    
    Преобразует триплеты из строк в числовые индексы для обучения модели
    """
    id_triples = []
    for head, rel, tail in triples:
        if head in entity_to_id and tail in entity_to_id and rel in relation_to_id:
            id_triples.append((entity_to_id[head], relation_to_id[rel], entity_to_id[tail]))
    
    return id_triples


class TransE:
    """
    МОДЕЛЬ TransE (Translating Embeddings)
    
    Простая и эффективная модель для Knowledge Graph Embeddings.
    
    Идея:
    - Каждая сущность (entity) представлена вектором
    - Каждое отношение (relation) представлено вектором перевода
    - Для триплета (h, r, t): h + r ≈ t
    
    Score function: -||h + r - t||
    Чем выше score, тем более вероятен триплет
    """
    
    def __init__(self, num_entities: int, num_relations: int, embedding_dim: int = 64):
        """
        Инициализация модели
        
        Args:
            num_entities: количество сущностей
            num_relations: количество отношений
            embedding_dim: размерность embeddings
        """
        self.num_entities = num_entities
        self.num_relations = num_relations
        self.embedding_dim = embedding_dim
        
        # Инициализация embeddings (Xavier uniform)
        bound = 6.0 / math.sqrt(embedding_dim)
        self.entity_embeddings = np.random.uniform(-bound, bound, (num_entities, embedding_dim))
        self.relation_embeddings = np.random.uniform(-bound, bound, (num_relations, embedding_dim))
        
        # Нормализация
        self.entity_embeddings = self.entity_embeddings / np.linalg.norm(self.entity_embeddings, axis=1, keepdims=True)
        self.relation_embeddings = self.relation_embeddings / np.linalg.norm(self.relation_embeddings, axis=1, keepdims=True)
        
        print(f"\n✅ Модель TransE инициализирована:")
        print(f"   Сущностей: {num_entities}")
        print(f"   Отношений: {num_relations}")
        print(f"   Размерность embeddings: {embedding_dim}")
    
    def score(self, h: int, r: int, t: int) -> float:
        """
        ВЫЧИСЛЕНИЕ SCORE ДЛЯ ТРИПЛЕТА
        
        Score = -||h + r - t||
        Чем выше score, тем более вероятен триплет
        """
        h_vec = self.entity_embeddings[h]
        r_vec = self.relation_embeddings[r]
        t_vec = self.entity_embeddings[t]
        
        # h + r - t
        diff = h_vec + r_vec - t_vec
        
        # L2 норма (расстояние)
        distance = np.linalg.norm(diff)
        
        # Score (отрицательное расстояние - чем ближе, тем выше score)
        return -distance
    
    def train(self, triples: List[Tuple[int, int, int]], 
              num_epochs: int = 100,
              learning_rate: float = 0.0001,
              margin: float = 1.0,
              negative_ratio: int = 1,
              batch_size: int = 1000):
        """
        ОБУЧЕНИЕ МОДЕЛИ
        
        Использует margin ranking loss с negative sampling (sLCWA из лекции)
        
        Loss = max(0, margin - score(positive) + score(negative))
        """
        print("\n" + "="*80)
        print("ОБУЧЕНИЕ МОДЕЛИ TransE")
        print("="*80)
        print(f"   Эпох: {num_epochs}")
        print(f"   Learning rate: {learning_rate}")
        print(f"   Margin: {margin}")
        print(f"   Negative ratio: {negative_ratio}")
        print(f"   Batch size: {batch_size}")
        
        # Создаем множество всех триплетов для быстрой проверки
        triple_set = set(triples)
        
        # Создаем список всех сущностей для negative sampling
        all_entities = list(range(self.num_entities))
        
        for epoch in range(num_epochs):
            total_loss = 0.0
            num_batches = 0
            
            # Перемешиваем триплеты
            shuffled_triples = triples.copy()
            random.shuffle(shuffled_triples)
            
            # Обрабатываем батчами
            for i in range(0, len(shuffled_triples), batch_size):
                batch = shuffled_triples[i:i+batch_size]
                
                batch_loss = 0.0
                
                for h, r, t in batch:
                    # Positive triple score
                    pos_score = self.score(h, r, t)
                    
                    # Negative sampling
                    for _ in range(negative_ratio):
                        # Corrupt tail (заменяем tail на случайную сущность)
                        neg_t = random.choice(all_entities)
                        
                        # Проверяем, что это не настоящий триплет
                        while (h, r, neg_t) in triple_set:
                            neg_t = random.choice(all_entities)
                        
                        neg_score = self.score(h, r, neg_t)
                        
                        # Margin ranking loss
                        loss = max(0, margin - pos_score + neg_score)
                        batch_loss += loss
                        
                        if loss > 0:
                            # Градиентный спуск для TransE
                            # Loss = max(0, margin - score(pos) + score(neg))
                            # score = -||h + r - t||
                            # Градиент score по h: -(h + r - t) / ||h + r - t||
                            
                            h_vec = self.entity_embeddings[h].copy()
                            r_vec = self.relation_embeddings[r].copy()
                            t_pos_vec = self.entity_embeddings[t].copy()
                            t_neg_vec = self.entity_embeddings[neg_t].copy()
                            
                            # Вычисляем разности
                            diff_pos = h_vec + r_vec - t_pos_vec
                            diff_neg = h_vec + r_vec - t_neg_vec
                            
                            norm_pos = np.linalg.norm(diff_pos)
                            norm_neg = np.linalg.norm(diff_neg)
                            
                            # Избегаем деления на ноль
                            if norm_pos < 1e-8:
                                norm_pos = 1e-8
                            if norm_neg < 1e-8:
                                norm_neg = 1e-8
                            
                            # Градиенты (с правильным знаком для минимизации loss)
                            # Для loss = margin - score(pos) + score(neg)
                            # grad = -grad_score(pos) + grad_score(neg)
                            # grad_score = -diff / norm (для минимизации расстояния)
                            
                            grad_h = learning_rate * (diff_pos / norm_pos - diff_neg / norm_neg)
                            grad_r = learning_rate * (diff_pos / norm_pos - diff_neg / norm_neg)
                            grad_t_pos = -learning_rate * diff_pos / norm_pos
                            grad_t_neg = learning_rate * diff_neg / norm_neg
                            
                            # Обновляем embeddings
                            self.entity_embeddings[h] += grad_h
                            self.relation_embeddings[r] += grad_r
                            self.entity_embeddings[t] += grad_t_pos
                            self.entity_embeddings[neg_t] += grad_t_neg
                            
                            # НЕ нормализуем после каждого обновления - это мешает обучению
                            # Нормализация будет только периодически или в конце
                
                total_loss += batch_loss
                num_batches += 1
            
            avg_loss = total_loss / (num_batches * len(batch) * negative_ratio) if num_batches > 0 else 0
            
            # Периодическая нормализация (раз в 10 эпох) вместо после каждого обновления
            if (epoch + 1) % 10 == 0:
                # Нормализуем только entity embeddings, чтобы они не "разбегались"
                norms = np.linalg.norm(self.entity_embeddings, axis=1, keepdims=True)
                norms[norms < 1e-8] = 1.0  # Избегаем деления на ноль
                self.entity_embeddings = self.entity_embeddings / norms
            
            # Отслеживаем лучший loss
            if epoch == 0:
                best_loss = avg_loss
            elif avg_loss < best_loss:
                best_loss = avg_loss
            
            if (epoch + 1) % 10 == 0 or epoch == 0:
                trend = "📉" if avg_loss < best_loss else "📈" if avg_loss > best_loss else "➡️"
                print(f"   Эпоха {epoch + 1}/{num_epochs}: средний loss = {avg_loss:.4f} {trend} (лучший: {best_loss:.4f})")
                
                # Предупреждение если loss растет
                if epoch > 10 and avg_loss > best_loss * 1.5:
                    print(f"      ⚠️  ВНИМАНИЕ: Loss растет! Попробуйте уменьшить learning rate или увеличить margin")
        
        print(f"\n✅ Обучение завершено!")
    
    def predict_tail(self, h: int, r: int, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        ПРЕДСКАЗАНИЕ TAIL ДЛЯ (head, relation, ?)
        
        Вычисляет score для всех возможных tail и возвращает топ-k
        """
        scores = []
        for t in range(self.num_entities):
            score = self.score(h, r, t)
            scores.append((t, score))
        
        # Сортируем по убыванию score
        scores.sort(key=lambda x: -x[1])
        
        return scores[:top_k]
    
    def predict_head(self, r: int, t: int, top_k: int = 10) -> List[Tuple[int, float]]:
        """
        ПРЕДСКАЗАНИЕ HEAD ДЛЯ (?, relation, tail)
        
        Вычисляет score для всех возможных head и возвращает топ-k
        """
        scores = []
        for h in range(self.num_entities):
            score = self.score(h, r, t)
            scores.append((h, score))
        
        scores.sort(key=lambda x: -x[1])
        
        return scores[:top_k]


def create_kg_embeddings(limit: Optional[int] = None, 
                        embedding_dim: int = 64,
                        num_epochs: int = 50,
                        learning_rate: float = 0.0001):
    """
    СОЗДАНИЕ KNOWLEDGE GRAPH EMBEDDINGS
    
    Полный процесс:
    1. Извлечение триплетов из графа
    2. Создание индексов
    3. Обучение модели TransE
    4. Сохранение результатов
    """
    print("="*80)
    print("СОЗДАНИЕ KNOWLEDGE GRAPH EMBEDDINGS")
    print("="*80)
    
    # 1. Извлекаем триплеты
    triples = extract_triples_from_ontology()
    
    if limit:
        # Берем равномерно из всех типов отношений
        from collections import defaultdict
        triples_by_relation = defaultdict(list)
        for triple in triples:
            triples_by_relation[triple[1]].append(triple)
        
        # Берем по limit/N отношений из каждого типа
        limit_per_relation = max(1, limit // len(triples_by_relation))
        limited_triples = []
        for rel, rel_triples in triples_by_relation.items():
            limited_triples.extend(rel_triples[:limit_per_relation])
        
        triples = limited_triples
        print(f"\n⚠️  Ограничение: используем до {limit_per_relation} триплетов каждого типа")
    
    if len(triples) == 0:
        print("❌ Триплеты не найдены!")
        return None
    
    # 2. Создаем индексы
    entity_to_id, relation_to_id, id_to_entity, id_to_relation = create_entity_relation_mappings(triples)
    
    # 3. Конвертируем триплеты в индексы
    print("\n" + "="*80)
    print("КОНВЕРТАЦИЯ ТРИПЛЕТОВ В ИНДЕКСЫ")
    print("="*80)
    id_triples = convert_triples_to_ids(triples, entity_to_id, relation_to_id)
    print(f"✅ Конвертировано триплетов: {len(id_triples)}")
    
    # 4. Создаем и обучаем модель
    model = TransE(
        num_entities=len(entity_to_id),
        num_relations=len(relation_to_id),
        embedding_dim=embedding_dim
    )
    
    model.train(
        triples=id_triples,
        num_epochs=num_epochs,
        learning_rate=learning_rate,
        margin=1.0,
        negative_ratio=1,
        batch_size=min(1000, len(id_triples))
    )
    
    # 5. Сохраняем результаты
    output_dir = "kg_embeddings"
    os.makedirs(output_dir, exist_ok=True)
    
    # Сохраняем embeddings
    np.save(os.path.join(output_dir, "entity_embeddings.npy"), model.entity_embeddings)
    np.save(os.path.join(output_dir, "relation_embeddings.npy"), model.relation_embeddings)
    
    # Сохраняем индексы
    with open(os.path.join(output_dir, "entity_to_id.json"), 'w', encoding='utf-8') as f:
        json.dump(entity_to_id, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "relation_to_id.json"), 'w', encoding='utf-8') as f:
        json.dump(relation_to_id, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "id_to_entity.json"), 'w', encoding='utf-8') as f:
        json.dump(id_to_entity, f, ensure_ascii=False, indent=2)
    
    with open(os.path.join(output_dir, "id_to_relation.json"), 'w', encoding='utf-8') as f:
        json.dump(id_to_relation, f, ensure_ascii=False, indent=2)
    
    # Сохраняем модель (для дальнейшего использования)
    model_data = {
        'num_entities': model.num_entities,
        'num_relations': model.num_relations,
        'embedding_dim': model.embedding_dim
    }
    with open(os.path.join(output_dir, "model_info.json"), 'w') as f:
        json.dump(model_data, f, indent=2)
    
    print(f"\n✅ Все файлы сохранены в директории: {output_dir}/")
    print(f"   - entity_embeddings.npy: embeddings сущностей")
    print(f"   - relation_embeddings.npy: embeddings отношений")
    print(f"   - entity_to_id.json: индекс сущностей")
    print(f"   - relation_to_id.json: индекс отношений")
    
    return model, entity_to_id, relation_to_id, id_to_entity, id_to_relation


if __name__ == "__main__":
    import sys
    
    limit = None
    embedding_dim = 64
    num_epochs = 50
    
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
    
    create_kg_embeddings(
        limit=limit,
        embedding_dim=embedding_dim,
        num_epochs=num_epochs
    )

