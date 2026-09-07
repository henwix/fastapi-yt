import msgspec
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.configs import settings


def create_engine(db_url: str = settings.db_url, echo: bool = settings.debug) -> AsyncEngine:
    return create_async_engine(
        url=db_url,
        echo=echo,
        echo_pool=echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=settings.db_pool_pre_ping,
        json_serializer=lambda data: msgspec.json.encode(data).decode(),
        json_deserializer=msgspec.json.decode,
    )


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
