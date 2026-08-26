from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_comment_reactions.commands import CreateVideoCommentReactionCommand
from app.domain.channels.service import IChannelService
from app.domain.video_comment_reactions.entities import VideoCommentReaction
from app.domain.video_comment_reactions.service import IVideoCommentReactionService
from app.domain.video_comments.service import IVideoCommentService


@dataclass
class CreateVideoCommentReactionUseCase:
    _channel_service: IChannelService
    _video_comment_service: IVideoCommentService
    _video_comment_reaction_service: IVideoCommentReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoCommentReactionCommand) -> VideoCommentReaction | None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video_comment = await self._video_comment_service.try_get_by_id(id=command.video_comment_id)
        video_comment_reaction_entity = VideoCommentReaction.create(
            video_comment_id=video_comment.id,
            channel_id=channel.id,
            reaction_type=command.reaction_type,
        )
        async with self._transaction_manager:
            return await self._video_comment_reaction_service.upsert(
                video_comment_reaction=video_comment_reaction_entity
            )
