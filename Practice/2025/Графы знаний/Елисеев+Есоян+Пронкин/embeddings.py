import os
import json
import pickle
import argparse

import numpy as np
import rdflib
import torch
from pykeen.models import TransE
from pykeen.pipeline import pipeline
from pykeen.triples import TriplesFactory

# Пытаемся импортировать torch-directml для поддержки AMD/Intel GPU
try:
    import torch_directml
except ImportError:
    torch_directml = None

# Опциональные зависимости для визуализации
try:
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

try:
    from sklearn.manifold import TSNE
    from sklearn.decomposition import PCA
except ImportError:
    TSNE = None
    PCA = None


# ==========================
# 1. Обучение эмбеддингов
# ==========================

def train_graph_embeddings(ttl_file_path: str,
                           save_dir: str = "movie_embedding_results"):
    """
    Обучение TransE-эмбеддингов для RDF-графа.
    ttl_file_path — путь к Turtle-файлу (tmdb_data.ttl по умолчанию).
    save_dir — папка для модели и артефактов.
    """
    print(f"1. Загрузка графа из {ttl_file_path}...")
    g = rdflib.Graph()
    g.parse(ttl_file_path, format="turtle")
    print(f"   Загружено триплетов: {len(g)}")

    print("2. Подготовка данных для PyKEEN...")
    triples = []
    for s, p, o in g:
        triples.append([str(s), str(p), str(o)])
    triples = np.array(triples, dtype=str)

    # TriplesFactory и сплит на train/test
    tf = TriplesFactory.from_labeled_triples(triples)
    training, testing = tf.split([0.8, 0.2], random_state=42)
    print(f"   Сущностей: {len(tf.entity_to_id)}, отношений: {len(tf.relation_to_id)}")

    # Выбор устройства
    if torch.cuda.is_available():
        device = "cuda"
        print("3. Обучение модели TransE (устройство: CUDA/NVIDIA)...")
    elif torch_directml is not None:
        device = torch_directml.device()
        print("3. Обучение модели TransE (устройство: DirectML/AMD-Intel)...")
    else:
        device = "cpu"
        print("3. Обучение модели TransE (устройство: CPU)...")

    os.makedirs(save_dir, exist_ok=True)

    result = pipeline(
        training=training,
        testing=testing,
        model="TransE",
        model_kwargs=dict(embedding_dim=50),     # размерность эмбеддингов
        training_kwargs=dict(num_epochs=30),     # число эпох
        random_seed=42,
        device=device,
    )

    print("   Обучение завершено.")

    # Сохраняем всё, что умеет PyKEEN
    result.save_to_directory(save_dir)

    # Отдельно сохраняем TriplesFactory (для маппинга ID <-> URI)
    tf_path = os.path.join(save_dir, "triples_factory.pkl")
    with open(tf_path, "wb") as f:
        pickle.dump(tf, f)
    print(f"4. Результаты сохранены в папку '{save_dir}'")

    return result.model, tf


# ==========================
# 2. Загрузка сохранённой модели
# ==========================

def load_saved_model(directory: str = "movie_embedding_results"):
    """
    Загрузка ранее обученной модели и TriplesFactory.
    """
    print(f"Попытка загрузки модели из '{directory}'...")

    model_path = os.path.join(directory, "trained_model.pkl")
    tf_path = os.path.join(directory, "triples_factory.pkl")
    metadata_path = os.path.join(directory, "metadata.json")

    if not (os.path.exists(model_path) and os.path.exists(tf_path)):
        print("  Сохранённая модель или triples_factory не найдены.")
        return None, None

    try:
        model = torch.load(model_path, map_location=torch.device("cpu"), weights_only=False)

        with open(tf_path, "rb") as f:
            tf = pickle.load(f)

        embedding_dim = None
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, "r", encoding="utf-8") as f:
                    metadata = json.load(f)
                embedding_dim = (
                    metadata.get("best_pipeline_result", {})
                    .get("pipeline", {})
                    .get("model_kwargs", {})
                    .get("embedding_dim")
                )
            except Exception:
                pass

        print("  Модель и данные успешно загружены.")
        if embedding_dim is not None:
            print(f"  Размерность эмбеддингов: {embedding_dim}")
        return model, tf
    except Exception as e:
        print(f"  Ошибка при загрузке: {e}")
        return None, None


# ==========================
# 3. Метрики качества
# ==========================

def print_evaluation_metrics(results_dir: str,
                             scope: str = "both",
                             scenario: str = "realistic"):
    """
    Вывести ключевые метрики ранжирования из results.json.
    scope — какая часть отчёта использовать (both/head/tail).
    scenario — optimistic/pessimistic/realistic.
    """
    results_path = os.path.join(results_dir, "results.json")
    if not os.path.exists(results_path):
        print(f"Файл с метриками не найден: {results_path}")
        return

    try:
        with open(results_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Не удалось прочитать {results_path}: {e}")
        return

    metrics = data.get("metrics", {})
    scope_section = metrics.get(scope, {})
    scenario_section = scope_section.get(scenario)
    if not scenario_section:
        print(f"В results.json нет секции '{scope}/{scenario}'.")
        return

    print(f"Файл метрик: {results_path}")
    print(f"Секция отчёта: {scope} / {scenario}")

    mr = scenario_section.get("arithmetic_mean_rank")
    mrr = scenario_section.get("inverse_harmonic_mean_rank")
    hits_1 = scenario_section.get("hits_at_1")
    hits_3 = scenario_section.get("hits_at_3")
    hits_5 = scenario_section.get("hits_at_5")
    hits_10 = scenario_section.get("hits_at_10")

    if mr is not None:
        print(f"  MR : {mr:.2f}")
    if mrr is not None:
        print(f"  MRR: {mrr:.4f}")
    if hits_1 is not None:
        print(f"  Hits@1 : {hits_1:.4f}")
    if hits_3 is not None:
        print(f"  Hits@3 : {hits_3:.4f}")
    if hits_5 is not None:
        print(f"  Hits@5 : {hits_5:.4f}")
    if hits_10 is not None:
        print(f"  Hits@10: {hits_10:.4f}")


# ==========================
# 4. Доступ к эмбеддингам
# ==========================

def get_embedding_for_entity(model: TransE,
                             triples_factory: TriplesFactory,
                             entity_uri: str):
    """
    Получить вектор эмбеддинга для конкретной сущности по её URI.
    """
    if entity_uri not in triples_factory.entity_to_id:
        print(f"Сущность {entity_uri} не найдена в словаре entity_to_id.")
        return None

    entity_id = triples_factory.entity_to_id[entity_uri]
    entity_id_tensor = torch.as_tensor([entity_id])

    with torch.no_grad():
        embedding = model.entity_representations[0](entity_id_tensor)

    return embedding.detach().cpu().numpy()[0]


def collect_all_embeddings(model: TransE,
                           triples_factory: TriplesFactory):
    """
    Вернуть массив всех эмбеддингов и список URI в том же порядке.
    """
    with torch.no_grad():
        tensor_embeddings = model.entity_representations[0](indices=None).detach()
    embeddings = tensor_embeddings.cpu().numpy()
    labels = [
        triples_factory.entity_id_to_label[i]
        for i in range(len(embeddings))
    ]
    return embeddings, labels


# ==========================
# 5. Снижение размерности (t-SNE / PCA)
# ==========================

def reduce_embeddings(embeddings,
                      method: str = "tsne",
                      random_state: int = 42,
                      perplexity: int = 30):
    """
    Сжать эмбеддинги в 2D с помощью t-SNE или PCA.
    """
    if method == "pca":
        if PCA is None:
            raise ImportError("Скрипт запущен без scikit-learn. Установи scikit-learn для PCA.")
        reducer = PCA(n_components=2, random_state=random_state)
    else:
        if TSNE is None:
            raise ImportError("Скрипт запущен без scikit-learn. Установи scikit-learn для t-SNE.")
        n_samples = len(embeddings)
        if n_samples < 2:
            raise ValueError("Слишком мало точек для t-SNE: нужно хотя бы 2 сущности.")
        safe_perplexity = min(perplexity, n_samples - 1)
        reducer = TSNE(
            n_components=2,
            random_state=random_state,
            perplexity=safe_perplexity,
            init="pca",
            learning_rate="auto",
        )

    return reducer.fit_transform(embeddings)


# ==========================
# 6. Визуализация
# ==========================

def plot_embeddings_2d(points_2d,
                       labels,
                       title: str = "Embedding map",
                       max_labels: int = 50,
                       save_path: str | None = None,
                       figsize=(10, 8)):
    """
    Простая визуализация 2D-точек с подписями для первых max_labels.
    """
    if plt is None:
        raise ImportError("matplotlib не установлен. Установи matplotlib для визуализации.")

    plt.figure(figsize=figsize)
    plt.scatter(points_2d[:, 0], points_2d[:, 1], s=12, alpha=0.6)

    def _shorten(uri: str) -> str:
        bases = {
            "http://example.org/film-rating#": "fr:",
        }
        for base, prefix in bases.items():
            if uri.startswith(base):
                return prefix + uri[len(base):]
        return uri

    for i, label in enumerate(labels[:max_labels]):
        short = _shorten(label)
        plt.annotate(short, (points_2d[i, 0], points_2d[i, 1]), fontsize=8, alpha=0.7)

    plt.title(title)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200)
        print(f"График сохранён в {save_path}")
    else:
        plt.show()


def visualize_embeddings(model: TransE,
                         triples_factory: TriplesFactory,
                         method: str = "tsne",
                         max_labels: int = 75,
                         save_path: str = "movie_embedding_results/embeddings.png",
                         perplexity: int = 30,
                         max_points: int = 1200,
                         random_state: int = 42):
    """
    Полный пайплайн:
    - собираем все эмбеддинги;
    - при необходимости делаем сэмплирование;
    - снижаем размерность;
    - рисуем.
    """
    print("5. Подготовка данных для визуализации...")
    embeddings, labels = collect_all_embeddings(model, triples_factory)

    if max_points and len(embeddings) > max_points:
        rng = np.random.default_rng(random_state)
        indices = rng.choice(len(embeddings), size=max_points, replace=False)
        embeddings = embeddings[indices]
        labels = [labels[i] for i in indices]
        print(f"   Всего сущностей: {len(triples_factory.entity_to_id)}, "
              f"визуализируем случайные {len(labels)}.")
    else:
        print(f"   Всего сущностей: {len(labels)}.")

    print(f"   Снижение размерности методом {method}...")
    points_2d = reduce_embeddings(embeddings, method=method, perplexity=perplexity)

    plot_embeddings_2d(
        points_2d,
        labels,
        title=f"KG embeddings ({method.upper()})",
        max_labels=max_labels,
        save_path=save_path,
    )


# ==========================
# 7. Поиск похожих сущностей
# ==========================

def find_similar_entities(model: TransE,
                          triples_factory: TriplesFactory,
                          entity_uri: str,
                          top_k: int = 5):
    """
    Найти top_k близких сущностей по евклидову расстоянию в пространстве TransE.
    """
    if entity_uri not in triples_factory.entity_to_id:
        print(f"Сущность {entity_uri} не найдена.")
        return

    target_id = triples_factory.entity_to_id[entity_uri]

    with torch.no_grad():
        all_embeddings = model.entity_representations[0](indices=None).detach()

    target_embedding = all_embeddings[target_id].unsqueeze(0)
    distances = torch.norm(all_embeddings - target_embedding, dim=1, p=2)

    values, indices = torch.topk(distances, k=top_k + 1, largest=False)

    print(f"\nСущности, похожие на {entity_uri}:")
    for value, idx in zip(values, indices):
        idx = idx.item()
        if idx == target_id:
            continue
        entity_label = triples_factory.entity_id_to_label[idx]
        print(f"  - {entity_label} (расстояние: {value.item():.4f})")


# ==========================
# 8. CLI-интерфейс
# ==========================

def main():
    parser = argparse.ArgumentParser(
        description="Обучение и визуализация эмбеддингов KG "
                    "(PyKEEN + TransE, по умолчанию для Фильмов)"
    )
    parser.add_argument(
        "--ttl",
        default="tmdb_data.ttl",
        help="Путь к Turtle-файлу с графом (по умолчанию tmdb_data.ttl)",
    )
    parser.add_argument(
        "--results-dir",
        default="movie_embedding_results",
        help="Папка для сохранения модели и графиков",
    )
    parser.add_argument(
        "--train",
        action="store_true",
        help="Принудительно обучить заново, не загружать сохранённую модель",
    )
    parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Вывести сохранённые метрики качества (results.json)",
    )
    parser.add_argument(
        "--metrics-scope",
        choices=["both", "head", "tail"],
        default="both",
        help="Какую часть отчёта PyKEEN использовать для вывода метрик",
    )
    parser.add_argument(
        "--metrics-scenario",
        choices=["realistic", "optimistic", "pessimistic"],
        default="realistic",
        help="Оптимистичный/реалистичный/пессимистичный сценарий для метрик",
    )
    parser.add_argument(
        "--entity",
        default="http://example.org/film-rating#movie/152601",
        help="URI сущности для вывода примера вектора",
    )
    parser.add_argument(
        "--similar",
        nargs="*",
        default=[
            "http://example.org/film-rating#movie/152601",
            "http://example.org/film-rating#cast/152601_1245_1",
        ],
        help="URI сущностей, для которых ищем похожие",
    )
    parser.add_argument(
        "--topk",
        type=int,
        default=5,
        help="Сколько похожих сущностей показывать",
    )
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Построить 2D-визуализацию эмбеддингов",
    )
    parser.add_argument(
        "--viz-method",
        choices=["tsne", "pca"],
        default="tsne",
        help="Метод снижения размерности для визуализации",
    )
    parser.add_argument(
        "--viz-max-labels",
        type=int,
        default=75,
        help="Сколько подписей наносить на график",
    )
    parser.add_argument(
        "--viz-path",
        default=None,
        help="Путь для сохранения PNG с графиком (по умолчанию в results-dir)",
    )
    parser.add_argument(
        "--viz-perplexity",
        type=int,
        default=30,
        help="Параметр perplexity для t-SNE",
    )
    parser.add_argument(
        "--viz-max-points",
        type=int,
        default=1200,
        help="Сколько точек максимум использовать для t-SNE/PCA (случайная выборка)",
    )

    args = parser.parse_args()

    ttl_file = args.ttl
    save_dir = args.results_dir

    # 1) Пытаемся загрузить сохранённую модель (если не указано --train)
    model, tf = (None, None)
    if not args.train:
        model, tf = load_saved_model(save_dir)

    # 2) Если не удалось загрузить — тренируем с нуля
    if model is None or tf is None:
        print("Запускаем обучение с нуля...")
        model, tf = train_graph_embeddings(ttl_file, save_dir=save_dir)

    # 3) Пример: вывести вектор для --entity
    if args.entity:
        vec = get_embedding_for_entity(model, tf, args.entity)
        if vec is not None:
            print(f"\nПример вектора для {args.entity}:")
            print(vec[:10], "... (показаны первые 10 компонент)")

    # 4) Пример: поиск похожих сущностей
    if args.similar:
        print("\n--- Поиск похожих сущностей ---")
        for uri in args.similar:
            find_similar_entities(model, tf, uri, top_k=args.topk)

    # 5) Визуализация, если запросили
    if args.visualize:
        viz_path = args.viz_path or os.path.join(
            save_dir, f"embeddings_{args.viz_method}.png"
        )
        try:
            visualize_embeddings(
                model,
                tf,
                method=args.viz_method,
                max_labels=args.viz_max_labels,
                save_path=viz_path,
                perplexity=args.viz_perplexity,
                max_points=args.viz_max_points,
            )
        except ImportError as e:
            print(f"Не удалось построить визуализацию: {e}")
            print("Установи зависимости: pip install matplotlib scikit-learn")
        except Exception as e:
            print(f"Ошибка при визуализации: {e}")

    # 6) Вывести метрики, если запросили
    if args.show_metrics:
        print("\n--- Метрики качества модели ---")
        print_evaluation_metrics(
            save_dir,
            scope=args.metrics_scope,
            scenario=args.metrics_scenario,
        )


if __name__ == "__main__":
    main()
