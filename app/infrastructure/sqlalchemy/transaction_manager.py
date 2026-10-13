from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.infrastructure.sqlalchemy.database import Database


@dataclass
class SQLAlchemyTransactionManager(ITransactionManager):
    _db: Database
    _session: AsyncSession

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()

    @asynccontextmanager
    async def begin(self, commit: bool) -> AsyncGenerator[None]:
        self._db.set_session(session=self._session)
        try:
            yield
            if commit:
                await self.commit()
        except Exception:
            await self.rollback()
            raise
        finally:
            self._db.set_session(session=None)
