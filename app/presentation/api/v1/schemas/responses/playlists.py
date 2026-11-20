from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from app.application.playlists.dto import DetailedPlaylist, PlaylistPreviewVideo, PreviewPlaylist
from app.domain.playlists.entities import Playlist
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class PlaylistOutSchema(BaseSchema):
    id: UUID
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime

    @staticmethod
    def from_entity(entity: Playlist) -> PlaylistOutSchema:
        return PlaylistOutSchema(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            privacy_status=entity.privacy_status,
            created_at=entity.created_at,
        )


class DetailedPlaylistOutSchema(BaseSchema):
    id: UUID
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime
    channel_name: str
    channel_slug: str
    channel_avatar_url: HttpUrl | None

    @staticmethod
    def from_dto(dto: DetailedPlaylist) -> DetailedPlaylistOutSchema:
        return DetailedPlaylistOutSchema(
            id=dto.id,
            title=dto.title,
            description=dto.description,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
            channel_avatar_url=dto.channel_avatar_url,
        )


class PreviewPlaylistOutSchema(BaseSchema):
    id: UUID
    title: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime

    @staticmethod
    def from_dto(dto: PreviewPlaylist) -> PreviewPlaylistOutSchema:
        return PreviewPlaylistOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
        )


class PlaylistPreviewVideoOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    added_at: datetime
    channel_name: str
    channel_slug: str
    video_thumbnail_url: HttpUrl | None

    @staticmethod
    def from_dto(dto: PlaylistPreviewVideo) -> PlaylistPreviewVideoOutSchema:
        return PlaylistPreviewVideoOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            views_count=dto.views_count,
            added_at=dto.added_at,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
            video_thumbnail_url=dto.video_thumbnail_url,
        )
