from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class Post(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    text: str
    channel_id: UUID
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(text: str, channel_id: UUID) -> Post:
        return Post(text=text, channel_id=channel_id)

    def update(self, text: str | Empty) -> None:
        if text is not Empty.UNSET:
            self.text = text
