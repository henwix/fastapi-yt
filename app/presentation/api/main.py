from fastapi import FastAPI

from app.core.configs import settings
from app.domain.common.exceptions import AppException
from app.presentation.api.exception_handler import exception_handler
from app.presentation.api.v1.router import v1_router


def create_app() -> FastAPI:
    app = FastAPI(title=settings.app_name)

    app.include_router(router=v1_router, prefix='/v1')

    app.add_exception_handler(AppException, exception_handler)

    return app
