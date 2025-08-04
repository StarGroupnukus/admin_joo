build:
	docker compose build

start:
	docker compose up -d

stop:
	docker compose down

logs:
	docker compose logs -f


remove:
	docker compose down -v --rmi local

restart:
	docker compose down
	docker compose up -d --build
watch:
	docker compose watch

#dev
build_dev:
	docker compose -f docker-compose.dev.yaml build

start_dev:
	docker compose -f docker-compose.dev.yaml up -d

stop_dev:
	docker compose -f docker-compose.dev.yaml down

logs_dev:
	docker compose -f docker-compose.dev.yaml logs -f

remove_dev:
	docker compose -f docker-compose.dev.yaml down -v --rmi local

restart_dev:
	docker compose -f docker-compose.dev.yaml down
	docker compose -f docker-compose.dev.yaml up -d --build
watch_dev:
	docker compose -f docker-compose.dev.yaml watch
