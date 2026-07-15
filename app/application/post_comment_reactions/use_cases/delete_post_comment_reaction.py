from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comment_reactions.commands import DeletePostCommentReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.post_comment_reactions.services import IPostCommentReactionService
from app.domain.post_comments.services import IPostCommentService


@dataclass
class DeletePostCommentReactionUseCase:
    _channel_service: IChannelService
    _post_comment_service: IPostCommentService
    _post_comment_reaction_service: IPostCommentReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeletePostCommentReactionCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        post_comment = await self._post_comment_service.try_get_by_id(id=command.post_comment_id)

        async with self._transaction_manager:
            await self._post_comment_reaction_service.try_delete_by_post_comment_id_and_channel_id(
                post_comment_id=post_comment.id,
                channel_id=channel.id,
            )
