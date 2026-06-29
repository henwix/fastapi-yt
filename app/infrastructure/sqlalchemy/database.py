from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from app.core.configs import settings


def create_engine(db_url: str = settings.db_url, echo: bool = settings.debug) -> AsyncEngine:
    return create_async_engine(url=db_url, echo=echo)


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(bind=engine, expire_on_commit=False)
