import asyncio
from collections.abc import AsyncGenerator
from functools import lru_cache
from logging import getLogger

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.infrastructure.di.container import (
    AppProvider,
    ReadersProvider,
    RepositoriesProvider,
    ServicesProvider,
    UseCasesProvider,
)
from app.infrastructure.sqlalchemy.database import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.models import *  # noqa F403
from app.infrastructure.sqlalchemy.models.base import BaseORM

logger = getLogger(__name__)


@pytest.fixture(scope='session')
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def postgres_url() -> AsyncGenerator[str]:
    postgres = PostgresContainer(
        image='postgres:18-alpine',
        username='test',
        password='test',
        dbname='test',
        driver='asyncpg',
    )

    try:
        postgres.start()
        postgres_url_ = postgres.get_connection_url()
        logger.info(f'postgres url: {postgres_url_}')
        yield postgres_url_
    finally:
        postgres.stop()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_db(postgres_url: str):
    engine = create_async_engine(url=postgres_url, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.drop_all)
        await conn.run_sync(BaseORM.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def container(postgres_url: str) -> AsyncGenerator[AsyncContainer]:
    class DatabaseProvider(Provider):
        @provide(scope=Scope.APP, provides=AsyncEngine)
        def engine(self) -> AsyncEngine:
            return create_engine(db_url=postgres_url, echo=True)

        @provide(scope=Scope.APP, provides=async_sessionmaker)
        def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
            return create_session_factory(engine=engine)

        @provide(scope=Scope.REQUEST, provides=AsyncSession)
        async def provide_async_session(self, session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession]:
            session = session_factory()
            yield session
            await session.close()

    @lru_cache(1)
    def get_container() -> AsyncContainer:
        return make_async_container(
            AppProvider(),
            DatabaseProvider(),
            RepositoriesProvider(),
            ReadersProvider(),
            ServicesProvider(),
            UseCasesProvider(),
        )

    container = get_container()
    yield container
    await container.close()
