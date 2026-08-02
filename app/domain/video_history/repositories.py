from abc import ABC, abstractmethod

from app.domain.video_history.entities import VideoHistoryItem


class IVideoHistoryItemRepository(ABC):
    @abstractmethod
    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem: ...
