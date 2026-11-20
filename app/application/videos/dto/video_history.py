from dataclasses import dataclass
from datetime import datetime

from app.application.common.dto.base import DTO
from app.domain.videos.enums import VideoPrivacyStatusEnum


@dataclass
class PreviewVideoHistory(DTO):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    watched_at: datetime
    channel_name: str
    channel_slug: str
    video_thumbnail_url: str | None
