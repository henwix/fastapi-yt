from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum


class PostsSortingFieldsEnum(StrEnum):
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class PostsSorting:
    sort_by: PostsSortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPostsQuery:
    channel_slug: str
    sorting: PostsSorting
    pagination: CursorPagination


@dataclass(kw_only=True, frozen=True)
class GetPostQuery:
    post_id: UUID
