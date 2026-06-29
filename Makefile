.PHONY: all

DC = docker compose
LOGS = docker logs
EXEC = docker exec -it
APP_DEV_FILE = docker_compose/backend.yaml
STORAGES_FILE = docker_compose/storages.yaml
APP_CONTAINER = fastapi-yt-backend-dev
DATABASE_CONTAINER = fastapi-yt-postgres-dev
ENV = --env-file .env


up:
	${DC} -f ${APP_DEV_FILE} ${ENV} -f ${STORAGES_FILE} ${ENV} up --build -d

logs:
	${LOGS} ${APP_CONTAINER} -f

down:
	${DC} -f ${APP_DEV_FILE} ${ENV} -f ${STORAGES_FILE} ${ENV} down

restart:
	${DC} -f ${APP_DEV_FILE} ${ENV} -f ${STORAGES_FILE} ${ENV} down && ${DC} -f ${APP_DEV_FILE} ${ENV} -f ${STORAGES_FILE} ${ENV} up --build -d

makemigrations:
	${EXEC} ${APP_CONTAINER} alembic revision --autogenerate -m "$(m)"

migrate:
	${EXEC} ${APP_CONTAINER} alembic upgrade head

downgrade:
	${EXEC} ${APP_CONTAINER} alembic downgrade -1

shell:
	${EXEC} ${APP_CONTAINER} python -m asyncio

test:
	 poetry run pytest -s
