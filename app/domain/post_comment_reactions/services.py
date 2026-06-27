from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.post_comment_reactions.entities import PostCommentReaction
from app.domain.post_comment_reactions.exceptions import PostCommentReactionNotFoundError
from app.domain.post_comment_reactions.repositories import IPostCommentReactionRepository


class IPostCommentReactionService(ABC):
    @abstractmethod
    async def get_by_post_comment_id_and_channel_id(
        self,
        post_comment_id: UUID,
        channel_id: UUID,
    ) -> PostCommentReaction | None: ...

    @abstractmethod
    async def create(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction: ...

    @abstractmethod
    async def try_update(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction: ...

    @abstractmethod
    async def try_delete_by_post_comment_id_and_channel_id(
        self,
        post_comment_id: UUID,
        channel_id: UUID,
    ) -> None: ...


@dataclass
class PostCommentReactionService(IPostCommentReactionService):
    _repo: IPostCommentReactionRepository

    async def get_by_post_comment_id_and_channel_id(
        self, post_comment_id: UUID, channel_id: UUID
    ) -> PostCommentReaction | None:
        return await self._repo.get_by_post_comment_id_and_channel_id(
            post_comment_id=post_comment_id, channel_id=channel_id
        )

    async def create(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction:
        return await self._repo.create(post_comment_reaction=post_comment_reaction)

    async def try_update(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction:
        updated_post_comment_reaction = await self._repo.update(post_comment_reaction=post_comment_reaction)
        if not updated_post_comment_reaction:
            raise PostCommentReactionNotFoundError(
                post_comment_id=post_comment_reaction.id,
                channel_id=post_comment_reaction.channel_id,
            )
        return updated_post_comment_reaction

    async def try_delete_by_post_comment_id_and_channel_id(
        self,
        post_comment_id: UUID,
        channel_id: UUID,
    ) -> None:
        is_deleted = await self._repo.delete_by_post_comment_id_and_channel_id(
            post_comment_id=post_comment_id,
            channel_id=channel_id,
        )
        if not is_deleted:
            raise PostCommentReactionNotFoundError(
                post_comment_id=post_comment_id,
                channel_id=channel_id,
            )
