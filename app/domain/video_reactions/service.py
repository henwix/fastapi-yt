from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_reactions.exceptions import VideoReactionNotFoundError
from app.domain.video_reactions.repository import IVideoReactionRepository


class IVideoReactionService(ABC):
    @abstractmethod
    async def upsert(self, video_reaction: VideoReaction) -> VideoReaction | None: ...

    @abstractmethod
    async def try_delete_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> None: ...


@dataclass
class VideoReactionService(IVideoReactionService):
    _repo: IVideoReactionRepository

    async def upsert(self, video_reaction: VideoReaction) -> VideoReaction | None:
        return await self._repo.upsert(video_reaction=video_reaction)

    async def try_delete_by_video_id_and_channel_id(self, video_id: str, channel_id: UUID) -> None:
        is_deleted = await self._repo.delete_by_video_id_and_channel_id(video_id=video_id, channel_id=channel_id)
        if not is_deleted:
            raise VideoReactionNotFoundError(video_id=video_id, channel_id=channel_id)
