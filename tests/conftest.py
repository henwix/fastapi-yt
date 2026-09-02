from collections.abc import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from dishka import AsyncContainer, Scope, make_async_container, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from testcontainers.postgres import PostgresContainer
from testcontainers.redis import RedisContainer

from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.oauth.interfaces.service import IOAuthServiceFactory
from app.core.configs import Settings, settings
from app.domain.videos.service import IVideoService
from app.infrastructure.di.container import (
    AppProvider,
    DatabaseProvider,
    OAuthProvider,
    ReadersProvider,
    ReposProvider,
    ServicesProvider,
    UseCasesProvider,
)
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.sqlalchemy.database import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.models import *  # noqa F403
from app.infrastructure.sqlalchemy.models.base import BaseORM
from tests.mocks.oauth.service import MockOAuthServiceFactory
from tests.mocks.s3_provider import MockS3Provider
from tests.mocks.video_service import MockVideoService


@pytest.fixture(scope='session')
def redis_url() -> Generator[str]:
    redis = RedisContainer(image='redis:8.8-alpine')
    try:
        redis.start()
        host = redis.get_container_host_ip()
        port = redis.get_exposed_port(6379)
        yield f'redis://{host}:{port}'
    finally:
        redis.stop()


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


@pytest.fixture(scope='session')
def mock_database_dishka_provider(postgres_url: str, redis_url: str) -> DatabaseProvider:
    class MockDatabaseProvider(DatabaseProvider):
        @provide(scope=Scope.APP, provides=AsyncEngine, override=True)
        async def engine(self) -> AsyncGenerator[AsyncEngine]:
            engine = create_engine(db_url=postgres_url, echo=False)
            yield engine
            await engine.dispose()

        @provide(scope=Scope.APP, provides=async_sessionmaker, override=True)
        def session_factory(self, engine: AsyncEngine) -> async_sessionmaker:
            return create_session_factory(engine=engine)

        @provide(scope=Scope.REQUEST, provides=AsyncSession, override=True)
        async def provide_async_session(self, session_factory: async_sessionmaker) -> AsyncGenerator[AsyncSession]:
            session = session_factory()
            yield session
            await session.close()

        @provide(scope=Scope.APP)
        async def provide_redis_client(self) -> AsyncGenerator[Redis]:
            redis = get_redis_client(redis_url=redis_url)
            yield redis
            await redis.aclose()

    return MockDatabaseProvider()


@pytest_asyncio.fixture(scope='session')
async def container(mock_database_dishka_provider: DatabaseProvider) -> AsyncGenerator[AsyncContainer]:
    container = make_async_container(
        AppProvider(),
        OAuthProvider(),
        mock_database_dishka_provider,
        ReposProvider(),
        ReadersProvider(),
        ServicesProvider(),
        UseCasesProvider(),
    )

    try:
        yield container
    finally:
        await container.close()


@pytest_asyncio.fixture(scope='session')
async def mock_container(mock_database_dishka_provider: DatabaseProvider) -> AsyncGenerator[AsyncContainer]:
    class MockAppProvider(AppProvider):
        mock_s3_provider = provide(MockS3Provider, scope=Scope.REQUEST, provides=IS3Provider, override=True)

    class MockOAuthProvider(OAuthProvider):
        mock_oauth_service_factory = provide(MockOAuthServiceFactory, provides=IOAuthServiceFactory, override=True)

    class MockServicesProvider(ServicesProvider):
        mock_video_service = provide(MockVideoService, provides=IVideoService, override=True)

    container = make_async_container(
        MockAppProvider(),
        MockOAuthProvider(),
        mock_database_dishka_provider,
        ReposProvider(),
        ReadersProvider(),
        MockServicesProvider(),
        UseCasesProvider(),
    )

    try:
        yield container
    finally:
        await container.close()


@pytest.fixture(scope='session', autouse=True)
def test_override_settings() -> None:
    settings.s3_avatars_key_prefix = 'test-avatar-prefix'
    settings.s3_videos_key_prefix = 'test-video-prefix'
    settings.s3_private_bucket_name = 'test-private-bucket'
    settings.s3_public_bucket_name = 'test-public-bucket'
    settings.s3_public_bucket_url = 'https://test-public-bucket.com'
    settings.s3_endpoint = 'https://test-s3-endpoint.com'
    settings.s3_access_key = '123'
    settings.s3_secret_key = '123'
    settings.frontend_origin = 'http://localhost/'
    settings.oauth_redirect_path = 'oauth/activation'
    settings.oauth_github_client_id = '123'
    settings.oauth_github_client_secret = '456'
    settings.oauth_google_client_id = '123'
    settings.oauth_google_client_secret = '456'


@pytest.fixture
def test_settings() -> Settings:
    return settings
