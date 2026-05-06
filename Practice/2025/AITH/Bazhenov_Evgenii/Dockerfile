FROM python:3.12-slim

ENV PATH="${PATH}:/home/appuser/.local/bin"

# Устанавливаем переменные окружения для Python и Poetry
ENV PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/home/appuser/.local' \
    POETRY_VERSION=1.8.3

RUN apt-get update && apt-get install --no-install-recommends -y \
    build-essential \
    curl \
    software-properties-common && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false && \
    apt-get clean -y && rm -rf /var/lib/apt/lists/*

# Устанавливаем Poetry
RUN curl -sSL https://install.python-poetry.org | python3 -

# Создаем директорию для кэша Poetry
RUN mkdir -p /var/cache/pypoetry

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы poetry.lock и pyproject.toml в контейнер
COPY poetry.lock pyproject.toml ./

# Устанавливаем зависимости проекта с помощью Poetry
RUN poetry install --no-interaction --no-ansi

COPY src ./src

COPY Makefile .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

CMD make streamlit
