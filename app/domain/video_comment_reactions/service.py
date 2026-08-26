from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.video_comment_reactions.entities import VideoCommentReaction
from app.domain.video_comment_reactions.exceptions import VideoCommentReactionNotFoundError
from app.domain.video_comment_reactions.repository import IVideoCommentReactionRepository


class IVideoCommentReactionService(ABC):
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
    async def try_update(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction: ...

    @abstractmethod
    async def try_delete_by_video_comment_id_and_channel_id(
        self,
        video_comment_id: UUID,
        channel_id: UUID,
    ) -> None: ...


@dataclass
class VideoCommentReactionService(IVideoCommentReactionService):
    _repo: IVideoCommentReactionRepository

    async def upsert(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction | None:
        return await self._repo.upsert(video_comment_reaction=video_comment_reaction)

    async def get_by_video_comment_id_and_channel_id(
        self, video_comment_id: UUID, channel_id: UUID
    ) -> VideoCommentReaction | None:
        return await self._repo.get_by_video_comment_id_and_channel_id(
            video_comment_id=video_comment_id, channel_id=channel_id
        )

    async def create(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction:
        return await self._repo.create(video_comment_reaction=video_comment_reaction)

    async def try_update(self, video_comment_reaction: VideoCommentReaction) -> VideoCommentReaction:
        updated_video_comment_reaction = await self._repo.update(video_comment_reaction=video_comment_reaction)
        if not updated_video_comment_reaction:
            raise VideoCommentReactionNotFoundError(
                video_comment_id=video_comment_reaction.id,
                channel_id=video_comment_reaction.channel_id,
            )
        return updated_video_comment_reaction

    async def try_delete_by_video_comment_id_and_channel_id(
        self,
        video_comment_id: UUID,
        channel_id: UUID,
    ) -> None:
        is_deleted = await self._repo.delete_by_video_comment_id_and_channel_id(
            video_comment_id=video_comment_id,
            channel_id=channel_id,
        )
        if not is_deleted:
            raise VideoCommentReactionNotFoundError(
                video_comment_id=video_comment_id,
                channel_id=channel_id,
            )
