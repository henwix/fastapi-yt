from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.post_reactions.entities import PostReaction


class IPostReactionRepository(ABC):
    @abstractmethod
    async def create(self, post_reaction: PostReaction) -> PostReaction: ...

    @abstractmethod
    async def get_by_post_id_and_channel_id(
        self,
        post_id: UUID,
        channel_id: UUID,
    ) -> PostReaction | None: ...

    @abstractmethod
    async def update(self, post_reaction: PostReaction) -> PostReaction | None: ...

    @abstractmethod
    async def delete_by_post_id_and_channel_id(self, post_id: UUID, channel_id: UUID) -> bool: ...
