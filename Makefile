.PHONY: up down logs build shell-db shell-backend

up:
	docker-compose up -d
	@echo "Services started. API at http://localhost:8000/docs, Frontend at http://localhost:3000"

down:
	docker-compose down

logs:
	docker-compose logs -f

build:
	docker-compose build --no-cache

shell-db:
	docker-compose exec postgres psql -U salon_user -d salon_scheduler

shell-backend:
	docker-compose exec backend bash

shell-redis:
	docker-compose exec redis redis-cli

migrate:
	docker-compose exec backend alembic upgrade head