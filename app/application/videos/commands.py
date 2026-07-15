from dataclasses import dataclass
from uuid import UUID

from app.domain.common.constants import Empty
from app.domain.videos.enums import VideoPrivacyStatusEnum


@dataclass(kw_only=True, frozen=True)
class CreateVideoMultipartUploadCommand:
    current_channel_id: UUID
    filename: str
    title: str
    description: str
    privacy_status: VideoPrivacyStatusEnum


@dataclass(kw_only=True, frozen=True)
class GenerateVideoPartUploadUrlCommand:
    current_channel_id: UUID
    key: str
    upload_id: str
    part_number: int


@dataclass(kw_only=True, frozen=True)
class CompleteVideoMultipartUploadCommand:
    current_channel_id: UUID
    key: str
    upload_id: str
    parts: list[dict]


@dataclass(kw_only=True, frozen=True)
class AbortVideoMultipartUploadCommand:
    current_channel_id: UUID
    key: str
    upload_id: str


@dataclass(kw_only=True, frozen=True)
class GenerateVideoDownloadUrlCommand:
    current_channel_id: UUID | None
    video_id: str


@dataclass(kw_only=True, frozen=True)
class DeleteVideoCommand:
    current_channel_id: UUID
    video_id: str


@dataclass(kw_only=True, frozen=True)
class GetVideoCommand:
    current_channel_id: UUID | None
    video_id: str


@dataclass(kw_only=True, frozen=True)
class UpdateVideoCommand:
    current_channel_id: UUID
    video_id: str
    title: str | Empty = Empty.UNSET
    description: str | Empty = Empty.UNSET
    privacy_status: VideoPrivacyStatusEnum | Empty = Empty.UNSET
