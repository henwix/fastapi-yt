from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.video_history.entities import VideoHistoryItem
from app.domain.video_history.exceptions import VideoHistoryEmptyError, VideoNotFoundInHistoryError
from app.domain.video_history.repository import IVideoHistoryRepository


class IVideoHistoryService(ABC):
    @abstractmethod
    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem: ...

    @abstractmethod
    async def try_delete(self, channel_id: UUID, video_id: str) -> None: ...

    @abstractmethod
    async def try_clear(self, channel_id: UUID) -> None: ...


@dataclass
class VideoHistoryService(IVideoHistoryService):
    _repo: IVideoHistoryRepository

    async def upsert(self, video_history_item: VideoHistoryItem) -> VideoHistoryItem:
        return await self._repo.upsert(video_history_item=video_history_item)

    async def try_delete(self, channel_id: UUID, video_id: str) -> None:
        is_deleted = await self._repo.delete(channel_id=channel_id, video_id=video_id)
        if not is_deleted:
            raise VideoNotFoundInHistoryError(channel_id=channel_id, video_id=video_id)

    async def try_clear(self, channel_id: UUID) -> None:
        is_cleared = await self._repo.clear(channel_id=channel_id)
        if not is_cleared:
            raise VideoHistoryEmptyError(channel_id=channel_id)
