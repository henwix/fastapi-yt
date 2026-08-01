from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum


@dataclass(frozen=True)
class DetailedVideoDTO(DTO):
    id: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum
    is_reported: bool
    created_at: datetime
    channel_id: UUID
    channel_name: str
    channel_slug: str


@dataclass(frozen=True)
class PersonalPreviewVideoDTO(DTO):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    upload_status: VideoUploadStatusEnum
    created_at: datetime


@dataclass(frozen=True)
class PreviewVideoDTO(DTO):
    id: str
    title: str
    created_at: datetime
    author_name: str
    author_slug: str
