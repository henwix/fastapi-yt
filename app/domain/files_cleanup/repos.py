from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.files_cleanup.entities import FileCleanup


class IFileCleanupRepo(ABC):
    @abstractmethod
    async def create(self, cleanup: FileCleanup) -> FileCleanup: ...

    @abstractmethod
    async def create_many(self, cleanups: list[FileCleanup]) -> None: ...

    @abstractmethod
    async def get_many_for_cleanup(self, limit: int) -> list[FileCleanup]: ...

    @abstractmethod
    async def delete_many(self, ids: list[UUID]) -> int: ...
