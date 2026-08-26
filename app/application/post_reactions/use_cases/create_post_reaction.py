from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_reactions.commands import CreatePostReactionCommand
from app.domain.channels.service import IChannelService
from app.domain.post_reactions.entities import PostReaction
from app.domain.post_reactions.service import IPostReactionService
from app.domain.posts.service import IPostService


@dataclass
class CreatePostReactionUseCase:
    _channel_service: IChannelService
    _post_service: IPostService
    _post_reaction_service: IPostReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreatePostReactionCommand) -> PostReaction | None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        post = await self._post_service.try_get_by_id(id=command.post_id)
        post_reaction_entity = PostReaction.create(
            post_id=post.id,
            channel_id=channel.id,
            reaction_type=command.reaction_type,
        )
        async with self._transaction_manager:
            return await self._post_reaction_service.upsert(post_reaction=post_reaction_entity)
