from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPlaylistQuery:
    current_channel_id: UUID | None
    playlist_id: UUID


class PlaylistsPreviewSortingFieldsEnum(StrEnum):
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class PlaylistsPreviewSorting:
    sort_by: PlaylistsPreviewSortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPersonalPlaylistsQuery:
    current_channel_id: UUID
    sorting: PlaylistsPreviewSorting
    pagination: CursorPagination


@dataclass(kw_only=True, frozen=True)
class GetChannelPlaylistsQuery:
    channel_slug: str
    sorting: PlaylistsPreviewSorting
    pagination: CursorPagination


class PlaylistVideosSortingFieldsEnum(StrEnum):
    ADDED_AT = 'added_at'
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class PlaylistVideosSorting:
    sort_by: PlaylistVideosSortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPlaylistVideosQuery:
    current_channel_id: UUID | None
    playlist_id: UUID
    sorting: PlaylistVideosSorting
    pagination: CursorPagination
