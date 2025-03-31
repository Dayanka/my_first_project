# Используем официальный Python образ (на 3.12-slim)
FROM python:3.12-slim

# Отключаем запись pyc-файлов и буферизацию вывода
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы с зависимостями в контейнер
COPY pyproject.toml poetry.lock /app/

# Устанавливаем Poetry и зависимости
RUN pip install --upgrade pip && pip install poetry
# Чтобы использовать системный интерпретатор вместо создания виртуального окружения в контейнере:
RUN poetry config virtualenvs.create false && poetry install --only main --no-root

# Копируем оставшийся код проекта
COPY . /app/

# Открываем порт 8000 (на котором будет работать сервер)
EXPOSE 8000

# Команда для запуска сервера
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

