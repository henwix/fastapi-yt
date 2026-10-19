from datetime import timedelta
from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, and_, delete, or_, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.domain.files_cleanup.exceptions import FileCleanupAlreadyCreatedError
from app.domain.files_cleanup.repos import IFileCleanupRepo
from app.infrastructure.sqlalchemy.models import FileCleanupORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo
from app.utils.datetime import get_current_utc_datetime


class FileCleanupRepo(SQLAlchemyRepo, IFileCleanupRepo):
    def _parse_db_error(self, error: DBAPIError, cleanup: FileCleanup) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'uq_file_cleanup':
                raise FileCleanupAlreadyCreatedError(s3_key=cleanup.s3_key, bucket=cleanup.bucket)
            case _:
                raise

    async def create(self, cleanup: FileCleanup) -> FileCleanup:
        model = FileCleanupORM.from_entity(entity=cleanup)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, cleanup=cleanup)
        return model.to_entity()

    async def create_many(self, cleanups: list[FileCleanup]) -> None:
        models = [FileCleanupORM.from_entity(entity=cleanup) for cleanup in cleanups]
        async with self._db.get_session(commit=True) as session:
            session.add_all(instances=models)
            await session.flush(objects=models)

    async def get_many_for_cleanup(self, limit: int) -> list[FileCleanup]:
        select_for_update_cleanups = (
            select(FileCleanupORM.id)
            .with_for_update(skip_locked=True)
            .where(
                or_(
                    FileCleanupORM.status == FileCleanupStatusEnum.PENDING,
                    and_(
                        FileCleanupORM.status == FileCleanupStatusEnum.PROCESSING,
                        FileCleanupORM.locked_until < get_current_utc_datetime(),
                    ),
                )
            )
            .limit(limit=limit)
        )
        stmt = (
            update(FileCleanupORM)
            .values(
                status=FileCleanupStatusEnum.PROCESSING,
                locked_until=get_current_utc_datetime() + timedelta(minutes=5),
            )
            .where(FileCleanupORM.id.in_(select_for_update_cleanups))
            .returning(FileCleanupORM)
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)

        return [cleanup.to_entity() for cleanup in result.scalars()]

    async def delete_many(self, ids: list[UUID]) -> int:
        stmt = delete(FileCleanupORM).where(FileCleanupORM.id.in_(ids))
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount

    async def update_many(
        self,
        ids: list[UUID],
        status: FileCleanupStatusEnum,
        error_code: str | None,
        error_message: str | None,
    ) -> int:
        stmt = (
            update(FileCleanupORM)
            .values(
                status=status.value,
                error_code=error_code,
                error_message=error_message,
            )
            .where(FileCleanupORM.id.in_(ids))
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount

    async def update_bulk(self, data: list[dict]) -> int:
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(
                statement=update(FileCleanupORM),
                params=data,
            )
        return cast(CursorResult, result).rowcount
