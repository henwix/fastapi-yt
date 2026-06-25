from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.post_comments.dto import DetailedPostCommentDTO
from app.application.post_comments.queries import PostCommentsSorting


class IPostCommentReader(ABC):
    @abstractmethod
    async def get_comments(
        self,
        post_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostCommentDTO]: ...

    @abstractmethod
    async def get_replies(
        self,
        post_comment_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostCommentDTO]: ...
