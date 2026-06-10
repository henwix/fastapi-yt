from dataclasses import dataclass

from app.application.commands.post_reactions import DeletePostReactionCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService
from app.domain.post_reactions.services import IPostReactionService
from app.domain.posts.services import IPostService


@dataclass
class DeletePostReactionUseCase:
    channel_service: IChannelService
    post_service: IPostService
    post_reaction_service: IPostReactionService
    transaction_manager: ITransactionManager

    async def execute(self, command: DeletePostReactionCommand) -> None:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            post = await self.post_service.try_get_by_id(id=command.post_id)
            await self.post_reaction_service.try_delete_by_post_id_and_channel_id(
                post_id=post.id,
                channel_id=channel.id,
            )
