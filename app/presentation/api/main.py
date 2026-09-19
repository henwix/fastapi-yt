from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.configs import settings
from app.infrastructure.di.container import get_container
from app.infrastructure.logging.config import configure_logging
from app.infrastructure.taskiq.broker import get_broker
from app.presentation.api.exceptions.exception_handler import ExceptionHandler
from app.presentation.api.responses.msgspec import MsgSpecJSONResponse
from app.presentation.api.v1.handlers import v1_router


def setup_di(app: FastAPI) -> None:
    container = get_container()
    setup_dishka(container=container, app=app)


def setup_routers(app: FastAPI) -> None:
    app.include_router(router=v1_router, prefix='/v1')


def setup_middlewares(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )


def setup_exception_handler(app: FastAPI) -> None:
    exception_handler = ExceptionHandler()
    exception_handler.setup_handler(app=app)


@asynccontextmanager
async def lifespan(app: FastAPI):
    broker = get_broker()
    if not broker.is_worker_process:
        await broker.startup()

    yield

    if not broker.is_worker_process:
        await broker.shutdown()
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    configure_logging()

    app = FastAPI(
        title=settings.app_name,
        lifespan=lifespan,
        default_response_class=MsgSpecJSONResponse,
    )

    setup_di(app=app)
    setup_routers(app=app)
    setup_middlewares(app=app)
    setup_exception_handler(app=app)

    return app
