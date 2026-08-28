from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum


@dataclass(frozen=True)
class DetailedVideo(DTO):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    is_reported: bool
    created_at: datetime
    views_count: int
    channel_id: UUID
    channel_name: str
    channel_slug: str


@dataclass(frozen=True)
class ChannelPreviewVideo(DTO):
    id: str
    title: str
    views_count: int
    created_at: datetime


@dataclass(frozen=True)
class PersonalPreviewVideo(DTO):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    upload_status: VideoUploadStatusEnum
    created_at: datetime
    views_count: int
