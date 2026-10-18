from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.infrastructure.sqlalchemy.models import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtDatetimeMixin, UUIDIdMixin


class FileCleanupORM(
    UUIDIdMixin,
    CreatedAtDatetimeMixin,
    BaseORM,
):
    __tablename__ = 'files_cleanup'

    s3_key: Mapped[str] = mapped_column(sa.String(length=255))
    bucket: Mapped[str] = mapped_column(sa.String(length=255))
    status: Mapped[str] = mapped_column(sa.String(length=10))
    locked_until: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True),
        default=None,
        server_default=sa.sql.null(),
    )
    error_code: Mapped[str | None] = mapped_column(default=None, server_default=sa.sql.null())
    error_message: Mapped[str | None] = mapped_column(default=None, server_default=sa.sql.null())

    __table_args__ = (
        sa.UniqueConstraint('s3_key', 'bucket', name='uq_file_cleanup'),
        sa.CheckConstraint("status IN ('pending', 'processing', 'failed')", name='ck_files_cleanup_status'),
    )

    @staticmethod
    def from_entity(entity: FileCleanup) -> FileCleanupORM:
        return FileCleanupORM(
            id=entity.id,
            s3_key=entity.s3_key,
            bucket=entity.bucket,
            status=entity.status,
            locked_until=entity.locked_until,
            created_at=entity.created_at,
        )

    def to_entity(self) -> FileCleanup:
        return FileCleanup(
            id=self.id,
            s3_key=self.s3_key,
            bucket=self.bucket,
            status=FileCleanupStatusEnum(self.status),
            locked_until=self.locked_until,
            created_at=self.created_at,
        )
