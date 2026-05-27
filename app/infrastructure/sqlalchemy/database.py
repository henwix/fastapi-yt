from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.configs import settings


class Database:
    def __init__(self) -> None:
        self._async_engine = create_async_engine(
            url=settings.db_url,
            echo=settings.debug,
            isolation_level='READ COMMITTED',
        )
        self._async_session = async_sessionmaker(
            bind=self._async_engine,
            expire_on_commit=False,
        )
        self._async_read_only_engine = create_async_engine(
            url=settings.db_url,
            echo=settings.debug,
            isolation_level='AUTOCOMMIT',
        )
        self._async_read_only_session = async_sessionmaker(
            bind=self._async_read_only_engine,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def get_session(self) -> AsyncGenerator[AsyncSession]:
        session = self._async_session()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    @asynccontextmanager
    async def get_read_only_session(self) -> AsyncGenerator[AsyncSession]:
        session = self._async_read_only_session()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
