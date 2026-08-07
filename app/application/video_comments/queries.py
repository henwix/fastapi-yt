from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum


class VideoCommentsSortingFieldsEnum(StrEnum):
    CREATED_AT = 'created_at'


@dataclass(kw_only=True, frozen=True)
class VideoCommentsSorting:
    sort_by: VideoCommentsSortingFieldsEnum
    order: SortingOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetVideoCommentsQuery:
    video_id: str
    sorting: VideoCommentsSorting
    pagination: CursorPagination


@dataclass(kw_only=True, frozen=True)
class GetVideoCommentRepliesQuery:
    video_comment_id: UUID
    sorting: VideoCommentsSorting
    pagination: CursorPagination
