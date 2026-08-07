from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_comments.commands import DeleteVideoCommentCommand
from app.domain.channels.services import IChannelService
from app.domain.video_comments.services import IVideoCommentService


@dataclass
class DeleteVideoCommentUseCase:
    _channel_service: IChannelService
    _video_comment_service: IVideoCommentService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoCommentCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video_comment = await self._video_comment_service.try_get_by_id(id=command.video_comment_id)
        self._video_comment_service.ensure_video_comment_access(video_comment=video_comment, channel=channel)

        async with self._transaction_manager:
            await self._video_comment_service.try_delete_by_id(id=video_comment.id)
