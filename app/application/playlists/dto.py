from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum


@dataclass
class DetailedPlaylistDTO(DTO):
    id: UUID
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime
    author_name: str
    author_slug: str
    videos_count: int


@dataclass
class PreviewPlaylistDTO(DTO):
    id: UUID
    title: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime
    videos_count: int


@dataclass
class PlaylistPreviewVideoDTO(DTO):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    added_at: datetime
    author_name: str
    author_slug: str
