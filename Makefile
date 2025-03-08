up:
	docker compose up -d --build

down:
	docker compose down

restart:
	docker compose down
	docker compose up -d --build

logs:
	docker compose logs -f

migrate:
	docker compose exec backend poetry run alembic upgrade head