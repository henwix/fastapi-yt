from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.files.entities import File
from app.domain.files.repos import IFileRepo


class IFileService(ABC):
    @abstractmethod
    async def create(self, file: File) -> File: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> File | None: ...

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> bool: ...


@dataclass
class FileService(IFileService):
    _repo: IFileRepo

    async def create(self, file: File) -> File:
        return await self._repo.create(file=file)

    async def get_by_id(self, id: UUID) -> File | None:
        return await self._repo.get_by_id(id=id)

    async def delete_by_id(self, id: UUID) -> bool:
        return await self._repo.delete_by_id(id=id)
