from abc import ABC, abstractmethod
from typing import Self


class ITransactionManager(ABC):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type, *_) -> None: ...
