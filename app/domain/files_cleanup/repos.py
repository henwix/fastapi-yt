from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.enums import FileCleanupStatusEnum


class IFileCleanupRepo(ABC):
    @abstractmethod
    async def upsert(self, cleanup: FileCleanup) -> bool: ...

    @abstractmethod
    async def upsert_many(self, cleanups: list[FileCleanup]) -> int: ...

    @abstractmethod
    async def get_many_for_cleanup(self, limit: int) -> list[FileCleanup]: ...

    @abstractmethod
    async def delete_many(self, ids: list[UUID]) -> int: ...

    @abstractmethod
    async def update_many(
        self,
        ids: list[UUID],
        status: FileCleanupStatusEnum,
        error_code: str | None,
        error_message: str | None,
    ) -> int: ...

    @abstractmethod
    async def update_bulk(self, data: list[dict]) -> int: ...
