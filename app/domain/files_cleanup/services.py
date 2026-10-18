from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.domain.files_cleanup.repos import IFileCleanupRepo


class IFileCleanupService(ABC):
    @abstractmethod
    async def create(self, cleanup: FileCleanup) -> FileCleanup: ...

    @abstractmethod
    async def create_many(self, cleanups: list[FileCleanup]) -> None: ...

    @abstractmethod
    async def get_for_cleanup(self, limit: int) -> list[FileCleanup]: ...

    @abstractmethod
    async def delete_many(self, ids: list[UUID]) -> int: ...

    @abstractmethod
    async def update_many(
        self,
        cleanups: list[FileCleanup],
        status: FileCleanupStatusEnum,
        error_code: str | None,
        error_message: str | None,
    ) -> int: ...

    @abstractmethod
    async def update_bulk(self, data: list[dict]) -> int: ...


@dataclass
class FileCleanupService(IFileCleanupService):
    _repo: IFileCleanupRepo

    async def create(self, cleanup: FileCleanup) -> FileCleanup:
        return await self._repo.create(cleanup=cleanup)

    async def create_many(self, cleanups: list[FileCleanup]) -> None:
        return await self._repo.create_many(cleanups=cleanups)

    async def get_for_cleanup(self, limit: int) -> list[FileCleanup]:
        return await self._repo.get_many_for_cleanup(limit=limit)

    async def delete_many(self, ids: list[UUID]) -> int:
        return await self._repo.delete_many(ids=ids)

    async def update_many(
        self,
        cleanups: list[FileCleanup],
        status: FileCleanupStatusEnum,
        error_code: str | None,
        error_message: str | None,
    ) -> int:
        return await self._repo.update_many(
            cleanups=cleanups, status=status, error_code=error_code, error_message=error_message
        )

    async def update_bulk(self, data: list[dict]) -> int:
        return await self._repo.update_bulk(data=data)
