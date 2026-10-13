from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class Database:
    def __init__(self, _session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory: async_sessionmaker[AsyncSession] = _session_factory
        self._session: AsyncSession | None = None

    def set_session(self, session: AsyncSession | None) -> None:
        self._session = session

    @asynccontextmanager
    async def get_session(self, commit: bool = False) -> AsyncGenerator[AsyncSession]:
        if self._session:
            yield self._session
            return

        async with self._session_factory() as session:
            try:
                yield session
                if commit:
                    await session.commit()
            except Exception:
                await session.rollback()
                raise
