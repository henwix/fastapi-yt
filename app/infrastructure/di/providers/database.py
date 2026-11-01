from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.sqlalchemy.config import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.database import Database
from app.infrastructure.sqlalchemy.transaction_manager import SQLAlchemyTransactionManager


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncEngine)
    async def engine(self) -> AsyncGenerator[AsyncEngine]:
        engine = create_engine()
        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP, provides=async_sessionmaker[AsyncSession])
    def session_factory(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(engine=engine)

    @provide(scope=Scope.REQUEST, provides=AsyncSession)
    async def provide_async_session(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> AsyncGenerator[AsyncSession]:
        async with session_factory() as session:
            yield session

    @provide(scope=Scope.APP)
    async def provide_redis_client(self) -> AsyncGenerator[Redis]:
        redis = get_redis_client()
        yield redis
        await redis.aclose()

    database = provide(Database, scope=Scope.REQUEST)
    transaction_manager = provide(SQLAlchemyTransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
