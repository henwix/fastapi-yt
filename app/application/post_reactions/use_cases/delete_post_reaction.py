from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_reactions.commands import DeletePostReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.post_reactions.services import IPostReactionService
from app.domain.posts.services import IPostService


@dataclass
class DeletePostReactionUseCase:
    _channel_service: IChannelService
    _post_service: IPostService
    _post_reaction_service: IPostReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeletePostReactionCommand) -> None:
        async with self._transaction_manager:
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
            post = await self._post_service.try_get_by_id(id=command.post_id)
            await self._post_reaction_service.try_delete_by_post_id_and_channel_id(
                post_id=post.id,
                channel_id=channel.id,
            )
