from pydantic import Field

from app.application.common.sorting import SortingOrderEnum
from app.application.playlists.queries import PlaylistsPreviewSortingFieldsEnum, PlaylistVideosSortingFieldsEnum
from app.domain.playlists.constants import (
    PLAYLISTS_DESCRIPTION_MAX_LENGTH,
    PLAYLISTS_TITLE_MAX_LENGTH,
    PLAYLISTS_TITLE_MIN_LENGTH,
)
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


class PlaylistsPreviewSortingParams(BaseSchema):
    sort_by: PlaylistsPreviewSortingFieldsEnum = PlaylistsPreviewSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class PlaylistVideosSortingParams(BaseSchema):
    sort_by: PlaylistVideosSortingFieldsEnum = PlaylistVideosSortingFieldsEnum.ADDED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
