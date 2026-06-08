from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.post_reactions.entities import PostReaction
from app.domain.post_reactions.exceptions import PostReactionNotFound
from app.domain.post_reactions.repository import IPostReactionRepository


class IPostReactionService(ABC):
    @abstractmethod
    async def create(self, post_reaction: PostReaction) -> PostReaction: ...

    @abstractmethod
    async def get_by_post_id_and_channel_id(
        self,
        post_id: UUID,
        channel_id: UUID,
    ) -> PostReaction | None: ...

    @abstractmethod
    async def try_update(self, post_reaction: PostReaction) -> PostReaction: ...

    @abstractmethod
    async def try_delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> None: ...


@dataclass
class PostReactionService(IPostReactionService):
    _post_reactions_repo: IPostReactionRepository

    async def create(self, post_reaction: PostReaction) -> PostReaction:
        return await self._post_reactions_repo.create(post_reaction=post_reaction)

    async def get_by_post_id_and_channel_id(
        self,
        post_id: UUID,
        channel_id: UUID,
    ) -> PostReaction | None:
        return await self._post_reactions_repo.get_by_post_id_and_channel_id(post_id=post_id, channel_id=channel_id)

    async def try_update(self, post_reaction: PostReaction) -> PostReaction:
        updated_post_reaction = await self._post_reactions_repo.update(post_reaction=post_reaction)
        if not updated_post_reaction:
            raise PostReactionNotFound(post_id=post_reaction.post_id, channel_id=post_reaction.channel_id)
        return updated_post_reaction

    async def try_delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> None:
        is_deleted = await self._post_reactions_repo.delete_by_post_id_and_channel_id(
            post_id=post_id,
            channel_id=channel_id,
        )
        if not is_deleted:
            raise PostReactionNotFound(post_id=post_id, channel_id=channel_id)
