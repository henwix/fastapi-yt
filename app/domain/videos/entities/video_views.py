from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_date


@dataclass(kw_only=True)
class VideoView(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    video_id: str
    channel_id: UUID | None
    anonymous_id: UUID | None
    views_count: int = 1
    created_at: date = field(default_factory=get_current_utc_date)

    @staticmethod
    def create(
        video_id: str,
        channel_id: UUID | None = None,
        anonymous_id: UUID | None = None,
    ) -> VideoView:
        return VideoView(
            video_id=video_id,
            channel_id=channel_id,
            anonymous_id=anonymous_id,
        )
