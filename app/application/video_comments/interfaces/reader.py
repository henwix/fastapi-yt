from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.video_comments.dto import DetailedVideoCommentDTO
from app.application.video_comments.queries import VideoCommentsSorting


class IVideoCommentReader(ABC):
    @abstractmethod
    async def get_comments(
        self,
        video_id: str,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: VideoCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedVideoCommentDTO]: ...

    @abstractmethod
    async def get_replies(
        self,
        video_comment_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: VideoCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedVideoCommentDTO]: ...
