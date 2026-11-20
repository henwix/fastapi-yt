from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto.base import DTO
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum


@dataclass
class DetailedPlaylist(DTO):
    id: UUID
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime
    channel_name: str
    channel_slug: str
    channel_avatar_url: str | None


@dataclass
class PreviewPlaylist(DTO):
    id: UUID
    title: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime


@dataclass
class PlaylistPreviewVideo(DTO):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    video_thumbnail_url: str | None
    added_at: datetime
    channel_name: str
    channel_slug: str
