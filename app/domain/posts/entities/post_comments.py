from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class PostComment(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    post_id: UUID
    channel_id: UUID
    reply_comment_id: UUID | None
    is_edited: bool = False
    text: str
    reply_level: int = 0
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(
        post_id: UUID,
        channel_id: UUID,
        reply_comment_id: UUID | None,
        reply_level: int,
        text: str,
    ) -> PostComment:
        return PostComment(
            post_id=post_id,
            channel_id=channel_id,
            reply_comment_id=reply_comment_id,
            text=text,
            reply_level=reply_level,
        )

    def set_text(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.text = value

    def set_is_edited(self, value: bool | Empty) -> None:
        if value is not Empty.UNSET:
            self.is_edited = value
