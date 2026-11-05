from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.files.entities import File


class IFileRepo(ABC):
    @abstractmethod
    async def create(self, file: File) -> File: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> File | None: ...

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> bool: ...
