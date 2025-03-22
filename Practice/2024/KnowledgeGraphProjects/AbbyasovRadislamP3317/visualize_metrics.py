import json
import matplotlib.pyplot as plt

# Загружаем метрики из сохранённого JSON
with open("metrics.json", "r") as f:
    metrics = json.load(f)

# Берем метрики из блока "both -> realistic"
results = metrics['both']['realistic']

# Извлекаем нужные значения
hits_at_1 = results['hits_at_1']
hits_at_3 = results['hits_at_3']
hits_at_5 = results['hits_at_5']
hits_at_10 = results['hits_at_10']
mr = results['arithmetic_mean_rank']

# Визуализация метрик
fig, axes = plt.subplots(1, 5, figsize=(15, 4))

# MR
axes[0].bar(['MR'], [mr])
axes[0].set_ylim(0, max(20, mr + 5))
axes[0].set_title('Mean Rank')

# Hits@1
axes[1].bar(['Hits@1'], [hits_at_1])
axes[1].set_ylim(0, 1)
axes[1].set_title('Hits@1')

# Hits@3
axes[2].bar(['Hits@3'], [hits_at_3])
axes[2].set_ylim(0, 1)
axes[2].set_title('Hits@3')

# Hits@5
axes[3].bar(['Hits@5'], [hits_at_5])
axes[3].set_ylim(0, 1)
axes[3].set_title('Hits@5')

# Hits@10
axes[4].bar(['Hits@10'], [hits_at_10])
axes[4].set_ylim(0, 1)
axes[4].set_title('Hits@10')

plt.suptitle("Результаты обучения модели TransE")
plt.tight_layout()
plt.show()
