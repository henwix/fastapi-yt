from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.repos import IFileCleanupRepo


class IFileCleanupService(ABC):
    @abstractmethod
    async def create(self, cleanup: FileCleanup) -> FileCleanup: ...

    @abstractmethod
    async def create_many(self, cleanups: list[FileCleanup]) -> None: ...


@dataclass
class FileCleanupService(IFileCleanupService):
    _repo: IFileCleanupRepo

    async def create(self, cleanup: FileCleanup) -> FileCleanup:
        return await self._repo.create(cleanup=cleanup)

    async def create_many(self, cleanups: list[FileCleanup]) -> None:
        return await self._repo.create_many(cleanups=cleanups)
