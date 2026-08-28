from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class Post(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    text: str
    channel_id: UUID
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(text: str, channel_id: UUID) -> Post:
        return Post(text=text, channel_id=channel_id)

    def set_text(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.text = value
