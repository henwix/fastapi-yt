from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPlaylistQuery:
    current_channel_id: UUID | None
    playlist_id: UUID


class GetPlaylistsPreviewSortingFieldsEnum(StrEnum):
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class GetPlaylistsPreviewSorting:
    sort_by: GetPlaylistsPreviewSortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPersonalPlaylistsQuery:
    current_channel_id: UUID
    sorting: GetPlaylistsPreviewSorting
    pagination: CursorPagination


@dataclass(kw_only=True, frozen=True)
class GetChannelPlaylistsQuery:
    channel_slug: str
    sorting: GetPlaylistsPreviewSorting
    pagination: CursorPagination
