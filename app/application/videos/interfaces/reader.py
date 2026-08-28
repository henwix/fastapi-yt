from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.videos.dto import ChannelPreviewVideo, DetailedVideo, PersonalPreviewVideo
from app.application.videos.queries import PersonalVideosFilters, PreviewVideosSorting


class IVideoReader(ABC):
    @abstractmethod
    async def try_get_detailed_video_by_id(self, id: str) -> DetailedVideo: ...

    @abstractmethod
    async def get_channel_videos(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | int | None,
        cursor_id_value: str | None,
        sorting: PreviewVideosSorting,
        pagination: CursorPagination,
    ) -> list[ChannelPreviewVideo]: ...

    @abstractmethod
    async def get_personal_videos(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | int | None,
        cursor_id_value: str | None,
        filters: PersonalVideosFilters,
        sorting: PreviewVideosSorting,
        pagination: CursorPagination,
    ) -> list[PersonalPreviewVideo]: ...
