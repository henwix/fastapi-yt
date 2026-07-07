from collections.abc import AsyncGenerator, Generator

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


@pytest.fixture(scope='session')
def postgres_url() -> Generator[str]:
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
        yield postgres_url_
    finally:
        postgres.stop()


@pytest_asyncio.fixture(scope='session', autouse=True)
async def setup_db(postgres_url: str):
    engine = create_async_engine(url=postgres_url, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(BaseORM.metadata.drop_all)
        await conn.run_sync(BaseORM.metadata.create_all)
    yield
    await engine.dispose()


@pytest_asyncio.fixture
async def container(postgres_url: str) -> AsyncGenerator[AsyncContainer]:
    class DatabaseProvider(Provider):
        @provide(scope=Scope.APP, provides=AsyncEngine)
        async def engine(self) -> AsyncGenerator[AsyncEngine]:
            engine = create_engine(db_url=postgres_url, echo=False)
            yield engine
            await engine.dispose()

        @provide(scope=Scope.APP, provides=async_sessionmaker)
        def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
            return create_session_factory(engine=engine)

        @provide(scope=Scope.REQUEST, provides=AsyncSession)
        async def provide_async_session(self, session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession]:
            session = session_factory()
            yield session
            await session.close()

    container = make_async_container(
        AppProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )

    yield container
    await container.close()
