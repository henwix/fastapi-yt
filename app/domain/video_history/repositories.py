from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.video_history.entities import VideoHistoryItem


class IVideoHistoryRepository(ABC):
    @abstractmethod
    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem: ...

    @abstractmethod
    async def delete(self, channel_id: UUID, video_id: str) -> bool: ...

    @abstractmethod
    async def clear(self, channel_id: UUID) -> bool: ...
