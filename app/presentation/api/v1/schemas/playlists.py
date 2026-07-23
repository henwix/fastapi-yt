from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.domain.playlists.constants import (
    PLAYLISTS_DESCRIPTION_MAX_LENGTH,
    PLAYLISTS_TITLE_MAX_LENGTH,
    PLAYLISTS_TITLE_MIN_LENGTH,
)
from app.domain.playlists.entities import Playlist
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
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
