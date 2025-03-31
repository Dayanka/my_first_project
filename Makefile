.PHONY: help build up down test migrate shell

help:
	@echo "Доступные команды:"
	@echo "  make build   - Собрать Docker-образы"
	@echo "  make up      - Запустить контейнеры в фоновом режиме"
	@echo "  make down    - Остановить и удалить контейнеры"
	@echo "  make test    - Запустить тесты Django"
	@echo "  make migrate - Применить миграции Django"
	@echo "  make shell   - Открыть Django shell внутри контейнера"

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

test:
	docker compose run web python manage.py test

migrate:
	docker compose run web python manage.py migrate

shell:
	docker compose run web python manage.py shell

