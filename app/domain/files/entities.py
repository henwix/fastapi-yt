from dataclasses import dataclass, field
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity


@dataclass(kw_only=True)
class File(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    key: str
    bucket: str

    @staticmethod
    def create(key: str, bucket: str) -> File:
        return File(key=key, bucket=bucket)
