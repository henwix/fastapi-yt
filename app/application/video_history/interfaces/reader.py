from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.video_history.dto import PreviewVideoHistoryDTO
from app.application.video_history.queries import VideoHistorySorting


class IVideoHistoryReader(ABC):
    @abstractmethod
    async def get_many(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: str | None,
        sorting: VideoHistorySorting,
        pagination: CursorPagination,
    ) -> list[PreviewVideoHistoryDTO]: ...
