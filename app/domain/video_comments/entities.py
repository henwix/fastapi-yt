from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class VideoComment(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    video_id: str
    channel_id: UUID
    reply_comment_id: UUID | None
    is_edited: bool = False
    text: str
    reply_level: int
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(
        video_id: str,
        channel_id: UUID,
        reply_comment_id: UUID | None,
        text: str,
        reply_level: int,
    ) -> VideoComment:
        return VideoComment(
            video_id=video_id,
            channel_id=channel_id,
            reply_comment_id=reply_comment_id,
            text=text,
            reply_level=reply_level,
        )

    def update(self, text: str | Empty) -> None:
        if text is not Empty.UNSET:
            self.text = text

        if not self.is_edited:
            self.is_edited = True
