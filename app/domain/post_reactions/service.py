from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.post_reactions.entities import PostReaction
from app.domain.post_reactions.exceptions import PostReactionNotFoundError
from app.domain.post_reactions.repo import IPostReactionRepo


class IPostReactionService(ABC):
    @abstractmethod
    async def upsert(self, post_reaction: PostReaction) -> PostReaction | None: ...

    @abstractmethod
    async def try_delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> None: ...


@dataclass
class PostReactionService(IPostReactionService):
    _repo: IPostReactionRepo

    async def upsert(self, post_reaction: PostReaction) -> PostReaction | None:
        return await self._repo.upsert(post_reaction=post_reaction)

    async def try_delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> None:
        is_deleted = await self._repo.delete_by_post_id_and_channel_id(
            post_id=post_id,
            channel_id=channel_id,
        )
        if not is_deleted:
            raise PostReactionNotFoundError(post_id=post_id, channel_id=channel_id)
