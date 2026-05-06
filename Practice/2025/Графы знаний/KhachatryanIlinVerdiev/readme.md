# WoW KG Embeddings (PyKEEN + TransE)

Небольшой скрипт для обучения эмбеддингов графа знаний World of Warcraft на базе PyKEEN/TransE и их визуализации.

## Быстрый старт
- Активируйте venv и поставьте зависимости (пример):  
  ```bash
  pip install rdflib pykeen torch matplotlib scikit-learn
  ```
- Убедитесь, что рядом лежит `wow_items_graph.ttl`.
- Запустить с автозагрузкой сохранённой модели (или обучением, если её нет):  
  ```bash
  python train_embeddings.py
  ```

## Полезные команды
- Принудительное обучение с нуля и сохранение артефактов в `wow_embedding_results`:  
  ```bash
  python train_embeddings.py --train
  ```
- Посчитать похожие сущности (смените URI под свои):  
  ```bash
  python train_embeddings.py \
    --similar http://example.org/wowkg#Sword http://example.org/wowkg#Class_Warrior \
    --topk 7
  ```
- Построить 2D-карту эмбеддингов (PCA быстрее t-SNE):  
  ```bash
  python train_embeddings.py --visualize --viz-method pca --viz-max-labels 40
  ```
  t-SNE с ограничением на количество точек:  
  ```bash
  python train_embeddings.py --visualize --viz-method tsne --viz-max-points 800 --viz-perplexity 20
  ```

## Ключевые флаги
- `--ttl` — путь к Turtle-файлу с графом (по умолчанию `wow_items_graph.ttl`).
- `--results-dir` — папка для модели и графиков (по умолчанию `wow_embedding_results`).
- `--entity` — какая сущность показывается как пример вектора.
- `--similar` / `--topk` — поиск похожих сущностей.
- `--visualize` + `--viz-method {tsne|pca}` + `--viz-max-labels` + `--viz-max-points` + `--viz-perplexity` — управление построением картинки (`--viz-path` для сохранения под другим именем).

## Заметки
- На macOS с MPS может появляться warning про `pin_memory` — его можно игнорировать.
- При сохранении/загрузке используется PyTorch 2.6+, поэтому в коде `torch.load(..., weights_only=False)` уже учтён. Если переносите модель, убедитесь, что доверяете исходному `trained_model.pkl`.
- Большинство URI внутри графа имеют вид `http://example.org/wowkg#Class_Warrior`, `...#Item_SomeName` и т.п. Если команда сообщает, что сущность не найдена, проверьте точный URI в TTL / через rdflib.
