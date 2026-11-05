import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.files.entities import File
from app.infrastructure.sqlalchemy.models import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import UUIDIdMixin


class FileORM(UUIDIdMixin, BaseORM):
    __tablename__ = 'files'

    key: Mapped[str]
    bucket: Mapped[str] = mapped_column(sa.String(length=64))

    __table_args__ = (sa.UniqueConstraint('key', 'bucket', name='uq_files_file'),)

    def to_entity(self) -> File:
        return File(
            id=self.id,
            key=self.key,
            bucket=self.bucket,
        )

    @staticmethod
    def from_entity(entity: File) -> FileORM:
        return FileORM(
            id=entity.id,
            key=entity.key,
            bucket=entity.bucket,
        )
