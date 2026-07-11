from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comments.commands import DeletePostCommentCommand
from app.domain.channels.services import IChannelService
from app.domain.post_comments.services import IPostCommentService


@dataclass
class DeletePostCommentUseCase:
    _channel_service: IChannelService
    _post_comment_service: IPostCommentService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeletePostCommentCommand) -> None:
        async with self._transaction_manager:
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
            post_comment = await self._post_comment_service.try_get_by_id(id=command.post_comment_id)
            self._post_comment_service.ensure_post_comment_access(post_comment=post_comment, channel=channel)
            await self._post_comment_service.try_delete_by_id(id=post_comment.id)
