from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl

from app.application.common.sorting import SortingOrderEnum
from app.application.playlists.dto import DetailedPlaylistDTO, PlaylistVideoDTO, PreviewPlaylistDTO
from app.application.playlists.queries import PlaylistsPreviewSortingFieldsEnum, PlaylistVideosSortingFieldsEnum
from app.domain.playlists.constants import (
    PLAYLISTS_DESCRIPTION_MAX_LENGTH,
    PLAYLISTS_TITLE_MAX_LENGTH,
    PLAYLISTS_TITLE_MIN_LENGTH,
)
from app.domain.playlists.entities import Playlist
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreatePlaylistInSchema(BaseSchema):
    title: str = Field(min_length=PLAYLISTS_TITLE_MIN_LENGTH, max_length=PLAYLISTS_TITLE_MAX_LENGTH)
    description: str = Field(max_length=PLAYLISTS_DESCRIPTION_MAX_LENGTH)
    privacy_status: PlaylistPrivacyStatusEnum


class UpdatePlaylistInSchema(BaseUpdateSchema):
    title: str = Field(default='', min_length=PLAYLISTS_TITLE_MIN_LENGTH, max_length=PLAYLISTS_TITLE_MAX_LENGTH)
    description: str = Field(default='', max_length=PLAYLISTS_DESCRIPTION_MAX_LENGTH)
    privacy_status: PlaylistPrivacyStatusEnum = PlaylistPrivacyStatusEnum.PUBLIC


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


class PlaylistsPreviewSortingParams(BaseSchema):
    sort_by: PlaylistsPreviewSortingFieldsEnum = PlaylistsPreviewSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


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


class PlaylistVideosSortingParams(BaseSchema):
    sort_by: PlaylistVideosSortingFieldsEnum = PlaylistVideosSortingFieldsEnum.ADDED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class PlaylistVideoOutSchema(BaseSchema):
    id: str
    title: str
    privacy_status: VideoPrivacyStatusEnum
    created_at: datetime
    added_at: datetime
    author_name: str
    author_slug: str

    @staticmethod
    def from_dto(dto: PlaylistVideoDTO) -> PlaylistVideoOutSchema:
        return PlaylistVideoOutSchema(
            id=dto.id,
            title=dto.title,
            privacy_status=dto.privacy_status,
            created_at=dto.created_at,
            added_at=dto.added_at,
            author_name=dto.author_name,
            author_slug=dto.author_slug,
        )


class PlaylistVideosCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[PlaylistVideoOutSchema]
