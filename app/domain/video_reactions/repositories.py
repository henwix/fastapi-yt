from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.video_reactions.entities import VideoReaction


class IVideoReactionRepository(ABC):
    @abstractmethod
    async def get_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> VideoReaction | None: ...

    @abstractmethod
    async def update(self, video_reaction: VideoReaction) -> VideoReaction | None: ...

    @abstractmethod
    async def create(self, video_reaction: VideoReaction) -> VideoReaction: ...

    @abstractmethod
    async def delete_by_video_id_and_channel_id(
        self,
        video_id: str,
        channel_id: UUID,
    ) -> bool: ...
