from abc import ABC, abstractmethod
from contextlib import AbstractAsyncContextManager


class ITransactionManager(ABC):
    @abstractmethod
    async def commit(self) -> None: ...

    @abstractmethod
    async def rollback(self) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

    @abstractmethod
    def begin(self, commit: bool) -> AbstractAsyncContextManager[None]: ...
