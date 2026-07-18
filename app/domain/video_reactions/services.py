from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_reactions.exceptions import VideoReactionNotFoundError
from app.domain.video_reactions.repositories import IVideoReactionRepository


class IVideoReactionService(ABC):
    @abstractmethod
    async def get_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> VideoReaction | None: ...

    @abstractmethod
    async def try_update(self, video_reaction: VideoReaction) -> VideoReaction: ...

    @abstractmethod
    async def create(self, video_reaction: VideoReaction) -> VideoReaction: ...

    @abstractmethod
    async def try_delete_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> None: ...


@dataclass
class VideoReactionService(IVideoReactionService):
    _repo: IVideoReactionRepository

    async def get_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> VideoReaction | None:
        return await self._repo.get_by_video_id_and_channel_id(video_id=video_id, channel_id=channel_id)

    async def try_update(self, video_reaction: VideoReaction) -> VideoReaction:
        updated_video_reaction = await self._repo.update(video_reaction=video_reaction)
        if not updated_video_reaction:
            raise VideoReactionNotFoundError(video_id=video_reaction.video_id, channel_id=video_reaction.channel_id)
        return updated_video_reaction

    async def create(self, video_reaction: VideoReaction) -> VideoReaction:
        return await self._repo.create(video_reaction=video_reaction)

    async def try_delete_by_video_id_and_channel_id(self, video_id: str, channel_id: UUID) -> None:
        is_deleted = await self._repo.delete_by_video_id_and_channel_id(video_id=video_id, channel_id=channel_id)
        if not is_deleted:
            raise VideoReactionNotFoundError(video_id=video_id, channel_id=channel_id)
