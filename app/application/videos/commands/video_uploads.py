from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class CreateVideoMultipartUploadCommand:
    current_channel_id: UUID
    video_id: str
    filename: str


@dataclass(kw_only=True, frozen=True)
class GenerateVideoPartUploadUrlCommand:
    current_channel_id: UUID
    video_id: str
    part_number: int


@dataclass(kw_only=True, frozen=True)
class CompleteVideoMultipartUploadCommand:
    current_channel_id: UUID
    video_id: str
    parts: list[dict]


@dataclass(kw_only=True, frozen=True)
class AbortVideoMultipartUploadCommand:
    current_channel_id: UUID
    video_id: str


@dataclass(kw_only=True, frozen=True)
class GenerateVideoThumbnailUploadUrlCommand:
    current_channel_id: UUID
    video_id: str
    filename: str


@dataclass(kw_only=True, frozen=True)
class ConfirmVideoThumbnailUploadCommand:
    current_channel_id: UUID
    video_id: str
    key: str


@dataclass(kw_only=True, frozen=True)
class GenerateVideoDownloadUrlCommand:
    current_channel_id: UUID | None
    video_id: str
