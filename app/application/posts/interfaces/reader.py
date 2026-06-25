from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.posts.dto import DetailedPostDTO
from app.application.posts.queries import PostsSorting


class IPostReader(ABC):
    @abstractmethod
    async def get_many(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostDTO]: ...
