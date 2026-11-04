from datetime import timedelta
from typing import cast
from uuid import UUID

from sqlalchemy import CursorResult, and_, delete, or_, select, update
from sqlalchemy.dialects.postgresql import insert

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.domain.files_cleanup.repos import IFileCleanupRepo
from app.infrastructure.sqlalchemy.models import FileCleanupORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo
from app.utils.datetime import get_current_utc_datetime


class FileCleanupRepo(SQLAlchemyRepo, IFileCleanupRepo):
    async def upsert(self, cleanup: FileCleanup) -> None:
        stmt = (
            insert(FileCleanupORM)
            .values(
                id=cleanup.id,
                s3_key=cleanup.s3_key,
                bucket=cleanup.bucket,
                status=cleanup.status,
                locked_until=cleanup.locked_until,
                created_at=cleanup.created_at,
            )
            .on_conflict_do_nothing(constraint='uq_files_cleanup_cleanup')
        )
        async with self._db.get_session(commit=True) as session:
            await session.execute(statement=stmt)

    async def upsert_many(self, cleanups: list[FileCleanup]) -> None:
        stmt = insert(FileCleanupORM).on_conflict_do_nothing(constraint='uq_files_cleanup_cleanup')
        async with self._db.get_session(commit=True) as session:
            await session.execute(
                statement=stmt,
                params=[
                    {
                        'id': cleanup.id,
                        's3_key': cleanup.s3_key,
                        'bucket': cleanup.bucket,
                        'status': cleanup.status.value,
                        'locked_until': cleanup.locked_until,
                        'created_at': cleanup.created_at,
                    }
                    for cleanup in cleanups
                ],
            )

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
