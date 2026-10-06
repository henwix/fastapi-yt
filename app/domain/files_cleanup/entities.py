from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class FileCleanup(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    s3_key: str
    bucket: str
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(s3_key: str, bucket: str) -> FileCleanup:
        return FileCleanup(s3_key=s3_key, bucket=bucket)
