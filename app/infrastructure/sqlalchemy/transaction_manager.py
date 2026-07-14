from dataclasses import dataclass
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.interfaces.transaction_manager import ITransactionManager


@dataclass
class SATransactionManager(ITransactionManager):
    _session: AsyncSession

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()

    async def close(self) -> None:
        await self._session.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, *_) -> None:
        if exc_type:
            await self.rollback()
            return
        await self.commit()
