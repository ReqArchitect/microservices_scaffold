up:
	docker-compose up --build -d

down:
	docker-compose down

migrate:
	docker-compose exec user_service flask db upgrade
	docker-compose exec auth_service flask db upgrade
	# ...repeat for each service...

health:
	curl -f http://localhost:8000/health
	curl -f http://localhost:5000/health
	# ...repeat for each service...

logs:
	docker-compose logs -f

backup:
	docker-compose exec postgres pg_dumpall -U micro > backup.sql

restore:
	docker-compose exec -T postgres psql -U micro < backup.sql

test:
	pytest

lint:
	flake8 .
	black --check .
	isort --check-only .
	mypy . 