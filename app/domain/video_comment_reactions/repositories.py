from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.video_comment_reactions.entities import VideoCommentReaction


class IVideoCommentReactionRepository(ABC):
    @abstractmethod
    async def upsert(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction | None: ...

    @abstractmethod
    async def get_by_video_comment_id_and_channel_id(
        self,
        video_comment_id: UUID,
        channel_id: UUID,
    ) -> VideoCommentReaction | None: ...

    @abstractmethod
    async def create(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction: ...

    @abstractmethod
    async def update(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction | None: ...

    @abstractmethod
    async def delete_by_video_comment_id_and_channel_id(
        self,
        video_comment_id: UUID,
        channel_id: UUID,
    ) -> bool: ...
