.PHONY: up down restart logs build test lint clean

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f

build:
	docker-compose build

test:
	docker-compose exec api pytest /app/tests
	docker-compose exec worker pytest /app/tests

lint:
	docker-compose exec api ruff check /app
	docker-compose exec worker ruff check /app

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type d -name ".pytest_cache" -exec rm -r {} +
