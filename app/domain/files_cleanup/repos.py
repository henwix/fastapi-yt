from abc import ABC, abstractmethod

from app.domain.files_cleanup.entities import FileCleanup


class IFileCleanupRepo(ABC):
    @abstractmethod
    async def create(self, cleanup: FileCleanup) -> FileCleanup: ...

    @abstractmethod
    async def create_many(self, cleanups: list[FileCleanup]) -> None: ...
