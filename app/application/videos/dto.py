from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO
from app.domain.videos.enums import VideoPrivacyStatusEnum


@dataclass(frozen=True)
class DetailedVideoDTO(DTO):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    s3_key: str
    is_reported: bool
    created_at: datetime
    channel_id: UUID
    channel_name: str
    channel_slug: str
