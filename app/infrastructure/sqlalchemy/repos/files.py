from typing import cast
from uuid import UUID

from sqlalchemy import CursorResult, delete, select

from app.domain.files.entities import File
from app.domain.files.repos import IFileRepo
from app.infrastructure.sqlalchemy.models import FileORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class FileRepo(SQLAlchemyRepo, IFileRepo):
    async def create(self, file: File) -> File:
        model = FileORM.from_entity(entity=file)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            await session.flush(objects=(model,))
        return model.to_entity()

    async def get_by_id(self, id: UUID) -> File | None:
        stmt = select(FileORM).where(FileORM.id == id)
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        file = result.scalar_one_or_none()
        return file.to_entity() if file is not None else None

    async def get_many_by_ids(self, ids: list[UUID]) -> list[File]:
        stmt = select(FileORM).where(FileORM.id.in_(ids))
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        files = result.scalars()
        return [file.to_entity() for file in files]

    async def delete_many_by_ids(self, ids: list[UUID]) -> int:
        stmt = delete(FileORM).where(FileORM.id.in_(ids))
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = delete(FileORM).where(FileORM.id == id)
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0
