from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl

from app.application.playlists.dto import DetailedPlaylistDTO, PlaylistPreviewVideoDTO, PreviewPlaylistDTO
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
    author_name: str
    author_slug: str
    videos_count: int = Field(ge=0)

    @staticmethod
    def from_dto(dto: DetailedPlaylistDTO) -> DetailedPlaylistOutSchema:
        return DetailedPlaylistOutSchema(
            id=dto.id,
            title=dto.title,
            description=dto.description,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            author_name=dto.author_name,
            author_slug=dto.author_slug,
            videos_count=dto.videos_count,
        )


class PreviewPlaylistOutSchema(BaseSchema):
    id: UUID
    title: str
    privacy_status: PlaylistPrivacyStatusEnum
    created_at: datetime
    videos_count: int = Field(ge=0)

    @staticmethod
    def from_dto(dto: PreviewPlaylistDTO) -> PreviewPlaylistOutSchema:
        return PreviewPlaylistOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            videos_count=dto.videos_count,
        )


class PreviewPlaylistsCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PreviewPlaylistOutSchema]


class PlaylistPreviewVideoOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    views_count: int
    added_at: datetime
    author_name: str
    author_slug: str

    @staticmethod
    def from_dto(dto: PlaylistPreviewVideoDTO) -> PlaylistPreviewVideoOutSchema:
        return PlaylistPreviewVideoOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            views_count=dto.views_count,
            added_at=dto.added_at,
            author_name=dto.author_name,
            author_slug=dto.author_slug,
        )


class PlaylistVideosCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PlaylistPreviewVideoOutSchema]
