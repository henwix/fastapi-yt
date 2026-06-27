from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.post_comment_reactions.entities import PostCommentReaction


class IPostCommentReactionRepository(ABC):
    @abstractmethod
    async def get_by_post_comment_id_and_channel_id(
        self,
        post_comment_id: UUID,
        channel_id: UUID,
    ) -> PostCommentReaction | None: ...

    @abstractmethod
    async def create(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction: ...

    @abstractmethod
    async def update(self, post_comment_reaction: PostCommentReaction) -> PostCommentReaction | None: ...

    @abstractmethod
    async def delete_by_post_comment_id_and_channel_id(
        self,
        post_comment_id: UUID,
        channel_id: UUID,
    ) -> bool: ...
