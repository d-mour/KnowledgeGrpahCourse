import os
import pickle
import argparse
import rdflib
from pykeen.triples import TriplesFactory
from pykeen.pipeline import pipeline
from pykeen.models import TransE
import torch
import numpy as np


# Пытаемся импортировать torch-directml для поддержки AMD карт
try:
    import torch_directml
except ImportError:
    torch_directml = None

# Попробуем подтянуть matplotlib/sklearn только если нужны,
# чтобы основной пайплайн обучения не зависел от них.
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


def train_graph_embeddings(ttl_file_path, save_dir='wow_embedding_results'):
    print(f"1. Загрузка графа из {ttl_file_path}...")
    g = rdflib.Graph()
    g.parse(ttl_file_path, format="turtle")
    print(f"   Загружено {len(g)} триплетов.")

    # Преобразуем триплеты rdflib в список строк для PyKEEN
    print("2. Подготовка данных для PyKEEN...")
    triples = []
    for s, p, o in g:
        # Конвертируем URI и литералы в строки
        triples.append([str(s), str(p), str(o)])
    
    triples = np.array(triples)

    # Создаем фабрику триплетов
    tf = TriplesFactory.from_labeled_triples(triples)

    # Разделяем на обучающую и тестовую выборки (80% / 20%)
    training, testing = tf.split([0.8, 0.2], random_state=42)

    print("3. Начало обучения модели TransE...")

    # Проверяем наличие GPU
    if torch.cuda.is_available():
        device = 'cuda'
        print("   Используется устройство: CUDA (NVIDIA)")
    elif torch_directml is not None:
        device = torch_directml.device()
        print("   Используется устройство: DirectML (AMD/Intel)")
    else:
        device = 'cpu'
        print("   Используется устройство: CPU")

    # Создаем папку для результатов
    os.makedirs(save_dir, exist_ok=True)

    # Запускаем пайплайн обучения
    result = pipeline(
        training=training,
        testing=testing,
        model='TransE',
        model_kwargs=dict(embedding_dim=50),  # Размерность вектора (длина списка чисел)
        training_kwargs=dict(num_epochs=50),  # Количество эпох обучения (можно увеличить)
        random_seed=42,
        device=device
    )

    print("   Обучение завершено.")
    
    # Сохраняем модель
    result.save_to_directory(save_dir)
    
    # Сохраняем фабрику триплетов (чтобы помнить маппинг ID <-> URI)
    with open(os.path.join(save_dir, 'triples_factory.pkl'), 'wb') as f:
        pickle.dump(tf, f)

    print(f"4. Результаты сохранены в папку '{save_dir}'")

    return result.model, tf

def load_saved_model(directory='wow_embedding_results'):
    """Загрузка обученной модели и фабрики триплетов"""
    print(f"Попытка загрузки модели из {directory}...")
    
    model_path = os.path.join(directory, 'trained_model.pkl')
    tf_path = os.path.join(directory, 'triples_factory.pkl')
    metadata_path = os.path.join(directory, 'metadata.json')

    if not os.path.exists(model_path) or not os.path.exists(tf_path):
        print("  Сохраненная модель не найдена.")
        return None, None

    try:
        # Загружаем модель (на CPU для совместимости).
        # В torch 2.6+ по умолчанию weights_only=True – нам нужен полный объект.
        model = torch.load(model_path, map_location=torch.device('cpu'), weights_only=False)
        
        # Загружаем фабрику
        with open(tf_path, 'rb') as f:
            tf = pickle.load(f)
        # Пытаемся получить размерность эмбеддингов из metadata, если есть
        embedding_dim = None
        if os.path.exists(metadata_path):
            try:
                import json
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                embedding_dim = metadata.get("best_pipeline_result", {}) \
                    .get("pipeline", {}) \
                    .get("model_kwargs", {}) \
                    .get("embedding_dim")
            except Exception:
                pass

        print("  Модель и данные успешно загружены!")
        if embedding_dim:
            print(f"  Размерность эмбеддингов: {embedding_dim}")
        return model, tf
    except Exception as e:
        print(f"  Ошибка при загрузке: {e}")
        return None, None


def get_embedding_for_entity(model, triples_factory, entity_uri):
    """Получить вектор для конкретной сущности"""
    # PyKEEN использует внутренние ID, нужно найти ID по URI
    if entity_uri in triples_factory.entity_to_id:
        entity_id = triples_factory.entity_to_id[entity_uri]
        # Получаем эмбеддинг (нужен torch.tensor)
        entity_id_tensor = torch.as_tensor([entity_id])
        embedding = model.entity_representations[0](entity_id_tensor)
        return embedding.detach().numpy()[0]
    else:
        print(f"Сущность {entity_uri} не найдена в словаре.")
        return None


def collect_all_embeddings(model, triples_factory):
    """Вернуть numpy-массив всех эмбеддингов и список URI в том же порядке"""
    with torch.no_grad():
        tensor_embeddings = model.entity_representations[0](indices=None).detach()
    embeddings = tensor_embeddings.cpu().numpy()
    labels = [triples_factory.entity_id_to_label[i] for i in range(len(embeddings))]
    return embeddings, labels


def reduce_embeddings(embeddings, method="tsne", random_state=42, perplexity=30):
    """
    Сжать эмбеддинги в 2D с помощью t-SNE или PCA.
    Возвращает массив shape (n, 2).
    """
    if method == "pca":
        if PCA is None:
            raise ImportError("sklearn не найден: установите scikit-learn для PCA")
        reducer = PCA(n_components=2, random_state=random_state)
    else:
        if TSNE is None:
            raise ImportError("sklearn не найден: установите scikit-learn для t-SNE")
        n_samples = len(embeddings)
        if n_samples < 2:
            raise ValueError("Слишком мало точек для t-SNE: нужно хотя бы 2 сущности")
        # t-SNE требует perplexity < n_samples, подстроим автоматически
        safe_perplexity = min(perplexity, n_samples - 1)
        reducer = TSNE(n_components=2, random_state=random_state, perplexity=safe_perplexity, init="pca", learning_rate="auto")
    return reducer.fit_transform(embeddings)


def plot_embeddings_2d(points_2d, labels, title="Embedding map", max_labels=50, save_path=None, figsize=(10, 8)):
    """Простая визуализация 2D-точек с подписями для первых `max_labels`"""
    if plt is None:
        raise ImportError("matplotlib не установлен. Установите matplotlib для визуализации.")

    plt.figure(figsize=figsize)
    plt.scatter(points_2d[:, 0], points_2d[:, 1], s=12, alpha=0.6)

    for i, label in enumerate(labels[:max_labels]):
        short = label.replace("http://example.org/wowkg#", "wow:")
        plt.annotate(short, (points_2d[i, 0], points_2d[i, 1]), fontsize=8, alpha=0.7)

    plt.title(title)
    plt.tight_layout()

    if save_path:
        plt.savefig(save_path, dpi=200)
        print(f"График сохранён в {save_path}")
    else:
        plt.show()


def visualize_embeddings(model, triples_factory, method="tsne", max_labels=75, save_path="wow_embedding_results/embeddings.png", perplexity=30, max_points=1200, random_state=42):
    """Общий пайплайн: собираем эмбеддинги -> снижаем размерность -> рисуем"""
    print("5. Подготовка данных для визуализации...")
    embeddings, labels = collect_all_embeddings(model, triples_factory)

    # Чтобы t-SNE не был слишком тяжелым, можно усечь до max_points случайных точек
    if max_points and len(embeddings) > max_points:
        rng = np.random.default_rng(random_state)
        indices = rng.choice(len(embeddings), size=max_points, replace=False)
        embeddings = embeddings[indices]
        labels = [labels[i] for i in indices]
        print(f"   Всего сущностей: {len(triples_factory.entity_to_id)}, визуализируем случайные {len(labels)}.")
    else:
        print(f"   Всего сущностей: {len(labels)}.")

    print(f"   Снижаем размерность методом {method}...")
    points_2d = reduce_embeddings(embeddings, method=method, perplexity=perplexity)
    plot_embeddings_2d(points_2d, labels, title=f"WoW KG embeddings ({method.upper()})", max_labels=max_labels, save_path=save_path)

def find_similar_entities(model, triples_factory, entity_uri, top_k=5):
    """Найти топ-K похожих сущностей"""
    if entity_uri not in triples_factory.entity_to_id:
        print(f"Сущность {entity_uri} не найдена.")
        return

    target_id = triples_factory.entity_to_id[entity_uri]
    
    # Получаем все эмбеддинги как тензор
    all_embeddings = model.entity_representations[0](indices=None).detach()
    target_embedding = all_embeddings[target_id].unsqueeze(0)

    # Вычисляем расстояния (чем меньше, тем более похожи)
    # TransE оптимизирует расстояния, поэтому используем Евклидову метрику
    distances = torch.norm(all_embeddings - target_embedding, dim=1, p=2)
    
    # Получаем индексы с наименьшим расстоянием
    # topk с largest=False даст нам наименьшие значения
    values, indices = torch.topk(distances, k=top_k+1, largest=False)
    
    print(f"\nСущности, похожие на {entity_uri}:")
    for value, idx in zip(values, indices):
        idx = idx.item()
        if idx == target_id:
            continue
            
        entity_label = triples_factory.entity_id_to_label[idx]
        print(f"  - {entity_label} (дистанция: {value.item():.4f})")

def main():
    parser = argparse.ArgumentParser(description="Обучение и визуализация эмбеддингов WoW KG (PyKEEN + TransE)")
    parser.add_argument("--ttl", default="wow_items_graph.ttl", help="Путь к Turtle-файлу с графом")
    parser.add_argument("--results-dir", default="wow_embedding_results", help="Папка для сохранения модели и графиков")
    parser.add_argument("--train", action="store_true", help="Принудительно обучить заново, не загружать сохраненную модель")
    parser.add_argument("--entity", default="http://example.org/wowkg#Item", help="URI сущности для вывода примера вектора")
    parser.add_argument("--similar", nargs="*", default=["http://example.org/wowkg#Sword", "http://example.org/wowkg#Class_Warrior"], help="URI сущностей, для которых ищем похожие")
    parser.add_argument("--topk", type=int, default=5, help="Сколько похожих сущностей показывать")
    parser.add_argument("--visualize", action="store_true", help="Построить 2D-визуализацию эмбеддингов")
    parser.add_argument("--viz-method", choices=["tsne", "pca"], default="tsne", help="Метод снижения размерности")
    parser.add_argument("--viz-max-labels", type=int, default=75, help="Сколько подписей наносить на график")
    parser.add_argument("--viz-path", default=None, help="Путь для сохранения PNG с графиком")
    parser.add_argument("--viz-perplexity", type=int, default=30, help="Параметр perplexity для t-SNE")
    parser.add_argument("--viz-max-points", type=int, default=1200, help="Сколько точек максимум использовать для t-SNE/PCA (случайная выборка)")
    args = parser.parse_args()

    ttl_file = args.ttl
    save_dir = args.results_dir

    # Пробуем загрузить существующую модель, если не просили тренировать заново
    model, tf = (None, None)
    if not args.train:
        model, tf = load_saved_model(save_dir)
    
    # Если не нашли или не смогли загрузить - тренируем заново
    if model is None or tf is None:
        print("Запускаем обучение с нуля...")
        model, tf = train_graph_embeddings(ttl_file, save_dir=save_dir)

    # Пример 1: Получить вектор
    if args.entity:
        vector = get_embedding_for_entity(model, tf, args.entity)
        if vector is not None:
            print(f"\nПример вектора для {args.entity}:")
            print(vector[:5], "... (показаны первые 5 чисел)")

    # Пример 2: Найти похожие сущности
    if args.similar:
        print("\n--- Проверка похожих сущностей ---")
        for uri in args.similar:
            find_similar_entities(model, tf, uri, top_k=args.topk)

    # Визуализация
    if args.visualize:
        viz_path = args.viz_path or os.path.join(save_dir, f"embeddings_{args.viz_method}.png")
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
            print("Установите зависимости: pip install matplotlib scikit-learn")
        except Exception as e:
            print(f"Ошибка при визуализации: {e}")


if __name__ == "__main__":
    main()
