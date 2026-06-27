from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_reactions.commands import CreatePostReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.post_reactions.entities import PostReaction
from app.domain.post_reactions.services import IPostReactionService
from app.domain.posts.services import IPostService


@dataclass
class CreatePostReactionUseCase:
    channel_service: IChannelService
    post_service: IPostService
    post_reaction_service: IPostReactionService
    transaction_manager: ITransactionManager

    async def execute(self, command: CreatePostReactionCommand) -> tuple[PostReaction, bool]:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            post = await self.post_service.try_get_by_id(id=command.post_id)
            post_reaction = await self.post_reaction_service.get_by_post_id_and_channel_id(
                post_id=post.id,
                channel_id=channel.id,
            )

            if post_reaction is not None:
                if post_reaction.reaction_type != command.reaction_type:
                    post_reaction.set_reaction_type(reaction_type=command.reaction_type)
                    post_reaction = await self.post_reaction_service.try_update(post_reaction=post_reaction)
                return post_reaction, False

            post_reaction_entity = PostReaction.create(
                post_id=command.post_id,
                channel_id=command.current_channel_id,
                reaction_type=command.reaction_type,
            )
            new_post_reaction = await self.post_reaction_service.create(post_reaction=post_reaction_entity)
            return new_post_reaction, True
