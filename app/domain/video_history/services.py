from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.video_history.entities import VideoHistoryItem
from app.domain.video_history.exceptions import VideoNotFoundInHistoryError
from app.domain.video_history.repositories import IVideoHistoryItemRepository


class IVideoHistoryItemService(ABC):
    @abstractmethod
    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem: ...

    @abstractmethod
    async def create(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem: ...

    @abstractmethod
    async def try_update(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem: ...

    @abstractmethod
    async def get_by_channel_id_and_video_id(self, channel_id: UUID, video_id: str) -> VideoHistoryItem | None: ...


@dataclass
class VideoHistoryItemService(IVideoHistoryItemService):
    _repo: IVideoHistoryItemRepository

    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem:
        return await self._repo.upsert(video_history_item=video_history_item)

    async def create(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem:
        return await self._repo.create(video_history_item=video_history_item)

    async def try_update(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem:
        updated_video_history_item = await self._repo.update(video_history_item=video_history_item)
        if updated_video_history_item is None:
            raise VideoNotFoundInHistoryError(
                channel_id=video_history_item.channel_id,
                video_id=video_history_item.video_id,
            )
        return updated_video_history_item

    async def get_by_channel_id_and_video_id(self, channel_id: UUID, video_id: str) -> VideoHistoryItem | None:
        return await self._repo.get_by_channel_id_and_video_id(channel_id=channel_id, video_id=video_id)
