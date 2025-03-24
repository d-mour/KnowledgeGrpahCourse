import pandas as pd
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory
import json

# Загружаем CSV с триплетами
df = pd.read_csv('clean_triples.csv')

# Готовим данные для PyKEEN
triplets = df.values

# Создаем TriplesFactory
tf = TriplesFactory.from_labeled_triples(triplets)

# Делаем сплит на train и test
train_tf, test_tf = tf.split([0.8, 0.2])

# Запуск пайплайна с TransE + RankBasedEvaluator
result = pipeline(
    model='TransE',
    training=train_tf,
    testing=test_tf,
    training_kwargs=dict(num_epochs=150),
    random_seed=42,
    evaluator='RankBasedEvaluator',
)

# Сохраняем модель и эмбеддинги
result.save_to_directory('embedding_output')

# Вывод метрик в консоль
metrics = result.metric_results
print(metrics.to_dict())

# Сохраняем метрики в JSON
with open("metrics.json", "w") as f:
    json.dump(metrics.to_dict(), f, indent=4)

print("Обучение завершено и метрики сохранены!")
