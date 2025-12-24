import owlready2 as owl
import pandas as pd
import numpy as np
import torch
from pykeen.models import TransE
from pykeen.training import SLCWATrainingLoop
from pykeen.regularizers import LpRegularizer
from pykeen.triples import TriplesFactory
from pykeen.evaluation import RankBasedEvaluator
from clusterization import perform_stat_clustering_analysis
from classification import perform_classification_analysis


def load_ontology(file_path):
    ontology = owl.get_ontology(file_path).load()
    return ontology

def parse_ontology_to_dataframe(ontology):
    accessories = []

    Accessory = ontology.search_one(iri="*Accessory")

    rarity_weights = {
        'Common': 1,
        'Uncommon': 2,
        'Rare': 3,
        'Epic': 4,
        'Legendary': 5
    }

    stat_props = ['hasDefense', 'hasHealth', 'hasStrength', 'hasIntelligence', 'hasCritDamage']
    req_props = ['requiresLevel', 'requiresCombatSkill', 'requiresMiningSkill',
                 'requiresFarmingSkill', 'requiresFishingSkill']

    for indiv in ontology.individuals():
        if isinstance(indiv, Accessory):
            accessory = {'name': indiv.name}

            for prop in indiv.get_properties():
                if prop.name == 'belongsToFamily':
                    family_values = list(prop[indiv])
                    if family_values:
                        accessory['family'] = family_values[0].name
                    else:
                        accessory['family'] = None
                    break
            else:
                accessory['family'] = None

            for prop in indiv.get_properties():
                if prop.name == 'hasRarity':
                    rarity_values = list(prop[indiv])
                    if rarity_values:
                        rarity_name = rarity_values[0].name
                        accessory['rarity'] = rarity_name
                        accessory['rarityWeight'] = rarity_weights.get(rarity_name, 0)
                    else:
                        accessory['rarity'] = None
                        accessory['rarityWeight'] = 0
                    break
            else:
                accessory['rarity'] = None
                accessory['rarityWeight'] = 0

            for prop_name in stat_props:
                for prop in indiv.get_properties():
                    if prop.name == prop_name:
                        values = list(prop[indiv])
                        accessory[prop_name] = int(values[0]) if values else 0
                        break
                else:
                    accessory[prop_name] = 0

            for prop_name in req_props:
                for prop in indiv.get_properties():
                    if prop.name == prop_name:
                        values = list(prop[indiv])
                        accessory[prop_name] = int(values[0]) if values else 0
                        break
                else:
                    accessory[prop_name] = 0

            accessories.append(accessory)

    df = pd.DataFrame(accessories)

    print(f"Количество записей: {len(df)}")
    print("Колонки:", list(df.columns))

    return df

def split_by_families(df, train_ratio=0.8):
    df_with_family = df[df['family'].notna()].copy()
    df_without_family = df[df['family'].isna()].copy()

    families = df_with_family['family'].unique()
    np.random.seed(42)
    np.random.shuffle(families)

    split_idx = int(len(families) * train_ratio)
    train_families = families[:split_idx]
    test_families = families[split_idx:]

    train_df_family = df_with_family[df_with_family['family'].isin(train_families)]
    test_df_family = df_with_family[df_with_family['family'].isin(test_families)]

    without_family_split_idx = int(len(df_without_family) * train_ratio)
    train_df_without_family = df_without_family.iloc[:without_family_split_idx]
    test_df_without_family = df_without_family.iloc[without_family_split_idx:]

    train_df = pd.concat([train_df_family, train_df_without_family])
    test_df = pd.concat([test_df_family, test_df_without_family])

    print(f"\nРазделение по семействам:")
    print(f"Всего семейств: {len(families)}")
    print(f"Обучающие семейства ({len(train_families)}): {train_families}")
    print(f"Тестовые семейства ({len(test_families)}): {test_families}")
    print(f"\nОбучающая выборка: {len(train_df)} записей")
    print(f"Тестовая выборка: {len(test_df)} записей")

    return train_df, test_df

def create_triplets_from_dataframe(df):
    all_triplets = []

    for _, row in df.iterrows():
        subject = row['name']

        if pd.notna(row['family']):
            all_triplets.append((subject, 'belongsToFamily', row['family']))

        if pd.notna(row['rarity']):
            all_triplets.append((subject, 'hasRarity', row['rarity']))
            all_triplets.append((row['rarity'], 'rarityWeight', str(row['rarityWeight'])))

        stat_props = ['hasDefense', 'hasHealth', 'hasStrength', 'hasIntelligence', 'hasCritDamage']
        for prop in stat_props:
            if prop in row and row[prop] > 0:
                all_triplets.append((subject, prop, str(row[prop])))

        req_props = ['requiresLevel', 'requiresCombatSkill', 'requiresMiningSkill',
                    'requiresFarmingSkill', 'requiresFishingSkill']
        for prop in req_props:
            if prop in row and row[prop] > 0:
                all_triplets.append((subject, prop, str(row[prop])))

    return all_triplets

def convert_to_knowledge_graph_format(train_df, test_df):
    print("\n=== ПРЕОБРАЗОВАНИЕ В ГРАФ ЗНАНИЙ ===")

    train_triplets = create_triplets_from_dataframe(train_df)
    test_triplets = create_triplets_from_dataframe(test_df)

    print(f"Триплеты обучающей выборки: {len(train_triplets)}")
    print(f"Триплеты тестовой выборки: {len(test_triplets)}")

    print("\nПримеры триплетов из обучающей выборки:")
    for i in range(min(10, len(train_triplets))):
        print(f"  {train_triplets[i]}")

    return train_triplets, test_triplets

def split_triplets_by_entities(train_triplets, val_ratio=0.2):
    all_entities = set()
    entity_to_triplets = {}
    
    for h, r, t in train_triplets:
        all_entities.add(h)
        all_entities.add(t)
        entity_to_triplets.setdefault(h, []).append((h, r, t))
        entity_to_triplets.setdefault(t, []).append((h, r, t))
    
    train_entities = list(all_entities)
    np.random.shuffle(train_entities)
    
    val_size = max(1, int(len(train_entities) * val_ratio))
    val_entities = set(train_entities[:val_size])
    
    train_train = []
    train_val = []
    
    entity_train_counts = {entity: 0 for entity in all_entities}
    entity_val_counts = {entity: 0 for entity in all_entities}
    
    for triple in train_triplets:
        h, r, t = triple
        in_val = (h in val_entities) or (t in val_entities)
        
        if in_val:
            train_val.append(triple)
            if h in val_entities:
                entity_val_counts[h] += 1
            if t in val_entities:
                entity_val_counts[t] += 1
        else:
            train_train.append(triple)
            entity_train_counts[h] += 1
            entity_train_counts[t] += 1
    
    for entity in val_entities:
        if entity_train_counts[entity] == 0:
            triple = entity_to_triplets[entity][0]
            if triple in train_val:
                train_val.remove(triple)
            train_train.append(triple)
            entity_train_counts[entity] += 1
            entity_val_counts[entity] -= 1
    
    for entity in all_entities:
        if entity_val_counts[entity] == 0 and entity not in val_entities:
            triple = entity_to_triplets[entity][0]
            if triple not in train_val:
                train_val.append(triple)
                entity_val_counts[entity] += 1
    
    print(f"\nРаспределение сущностей:")
    print(f"Всего сущностей: {len(all_entities)}")
    print(f"Сущностей в валидации: {len(val_entities)}")
    print(f"Сущностей с триплетами только в обучении: {sum(1 for e in all_entities if entity_train_counts[e] > 0 and entity_val_counts[e] == 0)}")
    print(f"Сущностей с триплетами в обоих наборах: {sum(1 for e in all_entities if entity_train_counts[e] > 0 and entity_val_counts[e] > 0)}")
    
    return train_train, train_val

def initialize_kge_model(train_train_triplets, train_val_triplets):
    entities = set()
    relations = set()
    
    for h, r, t in train_train_triplets + train_val_triplets:
        entities.add(h)
        entities.add(t)
        relations.add(r)
    
    entity_to_id = {entity: i for i, entity in enumerate(entities)}
    relation_to_id = {relation: i for i, relation in enumerate(relations)}
    
    # Тензор пайторча
    train_tensor = torch.LongTensor([
        [entity_to_id[h], relation_to_id[r], entity_to_id[t]]
        for h, r, t in train_train_triplets
    ])
    
    # Проприетарный пукиновский формат просто
    triples_factory = TriplesFactory(
        mapped_triples=train_tensor,
        entity_to_id=entity_to_id,
        relation_to_id=relation_to_id,
    )
    
    # Сама модель
    model = TransE(
        triples_factory=triples_factory,
        embedding_dim=200,
        # тип нормы (L2), сила регуляризации (ака learning rate)
        regularizer=LpRegularizer(p=2.0, weight=0.001),
        random_seed=124214124
    )
    
    return model, triples_factory

def train_kge_model(model, triples_factory, num_epochs=250, batch_size=32):
    from torch.optim import Adam
    
    optimizer = Adam(params=model.get_grad_params())
    training_loop = SLCWATrainingLoop(
        model=model,
        triples_factory=triples_factory,
        optimizer=optimizer,
    )
    
    training_loop.train(
        triples_factory=triples_factory,
        num_epochs=num_epochs,
        batch_size=batch_size,
    )
    
    return model

def evaluate_kge_model(model, triples_factory, test_triplets, all_train_triplets):
    entity_to_id = triples_factory.entity_to_id
    relation_to_id = triples_factory.relation_to_id
    
    test_mapped = []
    for h, r, t in test_triplets:
        if h in entity_to_id and r in relation_to_id and t in entity_to_id:
            test_mapped.append((
                entity_to_id[h],
                relation_to_id[r], 
                entity_to_id[t]
            ))
    
    if not test_mapped:
        print("ОШИБКА: Нет тестовых триплетов для оценки")
        return None
    
    test_tensor = torch.LongTensor(test_mapped)
    
    all_train_mapped = []
    for h, r, t in all_train_triplets:
        if h in entity_to_id and r in relation_to_id and t in entity_to_id:
            all_train_mapped.append((
                entity_to_id[h],
                relation_to_id[r],
                entity_to_id[t]
            ))
    
    all_train_tensor = torch.LongTensor(all_train_mapped)
    
    evaluator = RankBasedEvaluator(filtered=True)
    
    results = evaluator.evaluate(
        model=model,
        mapped_triples=test_tensor,
        additional_filter_triples=[all_train_tensor]
    )
    
    return results

def calculate_metrics(evaluation_results):
    metrics = {}
    
    metrics['mr'] = float(evaluation_results.get_metric('mean_rank'))
    metrics['mrr'] = float(evaluation_results.get_metric('mean_reciprocal_rank'))
    
    hits_at_n = {}
    for n in [1, 3, 5, 10]:
        hits_value = float(evaluation_results.get_metric(f'hits_at_{n}'))
        hits_at_n[n] = hits_value
    
    metrics['hits'] = hits_at_n
    
    return metrics

def print_evaluation_metrics(metrics):
    print("\nМЕТРИКИ ОЦЕНКИ:")
    print(f"MR (Mean Rank): {metrics['mr']:.1f}")
    print(f"MRR: {metrics['mrr']:.3f}")
    print("Hits@N:")
    for n, value in metrics['hits'].items():
        print(f"  @{n}: {value:.3f}")

def evaluate_model_pipeline(model, triples_factory, train_triplets, test_triplets):
    print("\n=== ОЦЕНКА МОДЕЛИ ===")
    
    results = evaluate_kge_model(
        model=model,
        triples_factory=triples_factory,
        test_triplets=test_triplets,
        all_train_triplets=train_triplets
    )
    
    if results is None:
        return
    
    metrics = calculate_metrics(results)
    print_evaluation_metrics(metrics)
    
    return metrics

def main():
    ontology = load_ontology("accessorizer-3000.owx")
    df = parse_ontology_to_dataframe(ontology)

    if len(df) == 0:
        print("НЕТ ДАННЫХ :(")
        return
        
    train_df, test_df = split_by_families(df)
    train_triplets, test_triplets = convert_to_knowledge_graph_format(train_df, test_df)

    np.random.seed(42)
    train_train_triplets, train_val_triplets = split_triplets_by_entities(train_triplets)
    kge_model, triples_factory = initialize_kge_model(train_train_triplets, train_val_triplets)
        
    trained_model = train_kge_model(
        model=kge_model,
        triples_factory=triples_factory,
        num_epochs=100,
        batch_size=256
    )
        
    print(f"\n{'='*50}")
    print("ОБУЧЕНИЕ ЗАВЕРШЕНО")
    print(f"{'='*50}")
        
    entity_embedding = trained_model.entity_representations[0]
    embedding_dim = entity_embedding._embeddings.weight.shape[1]
        
    relation_embedding = trained_model.relation_representations[0]
    relation_dim = relation_embedding._embeddings.weight.shape[1]
        
    print(f"\n РАЗМЕРНОСТИ ЭМБЕДДИНГОВ:")
    print(f"   Размерность эмбеддингов сущностей: {embedding_dim}")
    print(f"   Размерность эмбеддингов отношений: {relation_dim}")
        
    print(f"\n КОЛИЧЕСТВО ПАРАМЕТРОВ:")
    num_entities = trained_model.num_entities
    num_relations = trained_model.num_relations
    total_params = (num_entities * embedding_dim) + (num_relations * relation_dim)
    print(f"   Сущности: {num_entities} × {embedding_dim} = {num_entities * embedding_dim:,} параметров")
    print(f"   Отношения: {num_relations} × {relation_dim} = {num_relations * relation_dim:,} параметров")
    print(f"   Всего параметров: {total_params:,}")

    metrics = evaluate_model_pipeline(
        model=trained_model,
        triples_factory=triples_factory,
        train_triplets=train_triplets,
        test_triplets=test_triplets
    )
    print_evaluation_metrics(metrics)

    clustering_results = perform_stat_clustering_analysis(
        model=trained_model,
        triples_factory=triples_factory,
        ontology_df=df
    )

    classification_results = perform_classification_analysis(
        model=trained_model,
        triples_factory=triples_factory,
        ontology_df=df
    )

if __name__ == "__main__":
    main()
    