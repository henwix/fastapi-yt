from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum


class PostCommentsSortingFieldsEnum(StrEnum):
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class PostCommentsSorting:
    sort_by: PostCommentsSortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetPostCommentsQuery:
    post_id: UUID
    sorting: PostCommentsSorting
    pagination: CursorPagination


@dataclass(kw_only=True, frozen=True)
class GetPostCommentRepliesQuery:
    post_comment_id: UUID
    sorting: PostCommentsSorting
    pagination: CursorPagination
