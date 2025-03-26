# Используем официальный образ Python
FROM python:3.12-slim

# Устанавливаем рабочую директорию в контейнере
WORKDIR /app

# Копируем файлы проекта в контейнер
COPY . /app

# Устанавливаем зависимости из pyproject.toml
RUN pip install poetry
RUN poetry install --without dev

# Открываем порт для приложения (если нужно)
EXPOSE 8000

# Команда для запуска приложения
CMD ["poetry", "run", "python", "src/my_project/main.py"]

