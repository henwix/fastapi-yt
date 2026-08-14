from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.videos.dto import ChannelPreviewVideoDTO, DetailedVideoDTO, PersonalPreviewVideoDTO
from app.application.videos.queries import PersonalVideosFilters, PreviewVideosSorting


class IVideoReader(ABC):
    @abstractmethod
    async def try_get_detailed_video_by_id(self, id: str) -> DetailedVideoDTO: ...

    @abstractmethod
    async def get_channel_videos(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | int | None,
        cursor_id_value: str | None,
        sorting: PreviewVideosSorting,
        pagination: CursorPagination,
    ) -> list[ChannelPreviewVideoDTO]: ...

    @abstractmethod
    async def get_personal_videos(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | int | None,
        cursor_id_value: str | None,
        filters: PersonalVideosFilters,
        sorting: PreviewVideosSorting,
        pagination: CursorPagination,
    ) -> list[PersonalPreviewVideoDTO]: ...
