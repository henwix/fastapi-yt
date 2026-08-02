from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class VideoHistoryItem(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    channel_id: UUID
    video_id: str
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(channel_id: UUID, video_id: str) -> VideoHistoryItem:
        return VideoHistoryItem(channel_id=channel_id, video_id=video_id)

    def set_current_time_for_created_at(self) -> None:
        self.created_at = get_datetime_utc_now()
