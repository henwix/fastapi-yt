from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.videos.dto import DetailedVideoDTO, PersonalVideoDTO
from app.application.videos.queries import GetPersonalVideosFilters, GetPersonalVideosSorting


class IVideoReader(ABC):
    @abstractmethod
    async def try_get_detailed_by_id(self, id: str) -> DetailedVideoDTO: ...

    @abstractmethod
    async def get_personal_videos(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: str | None,
        filters: GetPersonalVideosFilters,
        sorting: GetPersonalVideosSorting,
        pagination: CursorPagination,
    ) -> list[PersonalVideoDTO]: ...
