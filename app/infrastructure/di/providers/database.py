from collections.abc import AsyncGenerator

from dishka import Provider, Scope, provide
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.infrastructure.redis.client import get_redis_client
from app.infrastructure.sqlalchemy.database import create_engine, create_session_factory
from app.infrastructure.sqlalchemy.transaction_manager import TransactionManager


class DatabaseProvider(Provider):
    @provide(scope=Scope.APP, provides=AsyncEngine)
    async def engine(self) -> AsyncGenerator[AsyncEngine]:
        engine = create_engine()
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

    @provide(scope=Scope.APP)
    async def provide_redis_client(self) -> AsyncGenerator[Redis]:
        redis = get_redis_client()
        yield redis
        await redis.aclose()

    transaction_manager = provide(TransactionManager, scope=Scope.REQUEST, provides=ITransactionManager)
