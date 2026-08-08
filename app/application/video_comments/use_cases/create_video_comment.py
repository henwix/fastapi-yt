from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_comments.commands import CreateVideoCommentCommand
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.video_comments.entities import VideoComment
from app.domain.video_comments.services import IVideoCommentService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.services import IVideoService


@dataclass
class CreateVideoCommentUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_comment_service: IVideoCommentService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoCommentCommand) -> VideoComment:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_completed_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            self._video_service.ensure_video_access(video=video, channel=channel)

        reply_comment = None
        if command.reply_comment_id is not Empty.UNSET:
            reply_comment = await self._video_comment_service.try_get_by_id_and_video_id(
                id=command.reply_comment_id,
                video_id=video.id,
            )

        comment_entity = VideoComment.create(
            video_id=video.id,
            channel_id=channel.id,
            reply_comment_id=reply_comment.id if reply_comment is not None else None,
            reply_level=reply_comment.reply_level + 1 if reply_comment is not None else 0,
            text=command.text,
        )

        async with self._transaction_manager:
            return await self._video_comment_service.create(video_comment=comment_entity)
