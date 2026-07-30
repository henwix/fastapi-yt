from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class VideoView(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    video_id: str
    channel_id: UUID
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(video_id: str, channel_id: UUID) -> VideoView:
        return VideoView(video_id=video_id, channel_id=channel_id)
