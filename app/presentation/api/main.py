from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI

from app.core.configs import settings
from app.domain.common.exceptions import AppException
from app.infrastructure.di.container import get_container
from app.presentation.api.exception_handler import exception_handler
from app.presentation.api.v1.router import v1_router


def init_di(app: FastAPI) -> None:
    container = get_container()
    setup_dishka(container=container, app=app)


def init_routers(app: FastAPI) -> None:
    app.include_router(router=v1_router, prefix='/v1')


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)
    app.add_exception_handler(AppException, exception_handler)

    init_di(app=app)
    init_routers(app=app)

    return app
