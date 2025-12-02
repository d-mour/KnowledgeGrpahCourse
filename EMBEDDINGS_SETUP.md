# Установка зависимостей для Embeddings

## Минимальные требования

Для работы системы embeddings нужны:

```bash
pip install numpy
```

## Опционально (для лучшей производительности)

```bash
pip install scikit-learn
```

Если `scikit-learn` не установлен, система будет использовать упрощенную версию нормализации и снижения размерности.

## Быстрая установка

```bash
# В виртуальном окружении
source venv/bin/activate
pip install numpy scikit-learn
```

## Проверка установки

```bash
python -c "import numpy; import sklearn; print('Все библиотеки установлены')"
```

## Использование

После установки зависимостей:

```bash
# Создать embeddings (тест на 100 автомобилях)
python create_embeddings.py --limit 100

# Создать embeddings для всех автомобилей
python create_embeddings.py

# Использовать поиск
python search_with_embeddings.py
```

