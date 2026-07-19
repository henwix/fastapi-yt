from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer

from app.application.common.interfaces.s3_provider import IS3Provider
from app.core.configs import settings
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
from tests.mocks.s3_provider import DummyS3Provider


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
    class MockAppProvider(AppProvider):
        s3_provider_mock = provide(DummyS3Provider, scope=Scope.REQUEST, provides=IS3Provider, override=True)

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
        MockAppProvider(),
        DatabaseProvider(),
        RepositoriesProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )

    yield container
    await container.close()


@pytest.fixture(scope='session', autouse=True)
def test_settings() -> None:
    settings.s3_avatars_key_prefix = 'test-avatar-prefix'
    settings.s3_videos_key_prefix = 'test-video-prefix'
    settings.s3_private_bucket_name = 'test-private-bucket'
    settings.s3_public_bucket_name = 'test-public-bucket'
    settings.s3_public_bucket_url = 'https://test-public-bucket.com'
    settings.s3_endpoint = 'https://test-s3-endpoint.com'
    settings.s3_access_key = '123'
    settings.s3_secret_key = '123'
