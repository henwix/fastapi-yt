from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.posts.dto import DetailedPost
from app.application.posts.queries import PostsSorting


class IPostReader(ABC):
    @abstractmethod
    async def get_many_by_channel_id(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPost]: ...

    @abstractmethod
    async def try_get_detailed_by_id(self, id: UUID) -> DetailedPost: ...
