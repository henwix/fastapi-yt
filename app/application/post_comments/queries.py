from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortOrderEnum


class PostCommentsSortFieldsEnum(StrEnum):
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class PostCommentsSorting:
    sort_by: PostCommentsSortFieldsEnum
    order: SortOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPostCommentsQuery:
    post_id: UUID
    sorting: PostCommentsSorting
    pagination: CursorPagination
