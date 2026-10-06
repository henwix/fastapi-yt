import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.files_cleanup.entities import FileCleanup
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

    __tableargs__ = (sa.UniqueConstraint('s3_key', 'bucket', name='uq_file_cleanup'),)

    @staticmethod
    def from_entity(entity: FileCleanup) -> FileCleanupORM:
        return FileCleanupORM(
            id=entity.id,
            s3_key=entity.s3_key,
            bucket=entity.bucket,
            created_at=entity.created_at,
        )

    def to_entity(self) -> FileCleanup:
        return FileCleanup(
            id=self.id,
            s3_key=self.s3_key,
            bucket=self.bucket,
            created_at=self.created_at,
        )
