from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.core.configs import settings
from app.domain.common.exceptions import AppException
from app.infrastructure.di.container import get_container
from app.infrastructure.logging.config import configure_logging
from app.infrastructure.taskiq.config import broker
from app.presentation.api.exception_handler import exception_handler
from app.presentation.api.v1.router import v1_router


def init_di(app: FastAPI) -> None:
    container = get_container()
    setup_dishka(container=container, app=app)


def init_routers(app: FastAPI) -> None:
    app.include_router(router=v1_router, prefix='/v1')


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.startup()
    yield
    await broker.shutdown()


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_exception_handler(AppException, exception_handler)

    init_di(app=app)
    init_routers(app=app)

    return app
