from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class VideoHistoryItem(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    channel_id: UUID
    video_id: str
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(channel_id: UUID, video_id: str) -> VideoHistoryItem:
        return VideoHistoryItem(channel_id=channel_id, video_id=video_id)
