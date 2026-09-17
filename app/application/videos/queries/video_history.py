from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum


class VideoHistorySortingFieldsEnum(StrEnum):
    WATCHED_AT = 'watched_at'


@dataclass(kw_only=True, frozen=True)
class VideoHistorySorting:
    sort_by: VideoHistorySortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetVideoHistoryQuery:
    current_channel_id: UUID
    sorting: VideoHistorySorting
    pagination: CursorPagination
