from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_comment_reactions.commands import CreateVideoCommentReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.video_comment_reactions.entities import VideoCommentReaction
from app.domain.video_comment_reactions.services import IVideoCommentReactionService
from app.domain.video_comments.services import IVideoCommentService


@dataclass
class CreateVideoCommentReactionUseCase:
    _channel_service: IChannelService
    _video_comment_service: IVideoCommentService
    _video_comment_reaction_service: IVideoCommentReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoCommentReactionCommand) -> tuple[VideoCommentReaction, bool]:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video_comment = await self._video_comment_service.try_get_by_id(id=command.video_comment_id)
        video_comment_reaction = await self._video_comment_reaction_service.get_by_video_comment_id_and_channel_id(
            video_comment_id=video_comment.id, channel_id=channel.id
        )

        async with self._transaction_manager:
            if video_comment_reaction is not None:
                if video_comment_reaction.reaction_type != command.reaction_type:
                    video_comment_reaction.set_reaction_type(reaction_type=command.reaction_type)
                    video_comment_reaction = await self._video_comment_reaction_service.try_update(
                        video_comment_reaction=video_comment_reaction
                    )
                return video_comment_reaction, False

            video_comment_reaction_entity = VideoCommentReaction.create(
                video_comment_id=video_comment.id,
                channel_id=channel.id,
                reaction_type=command.reaction_type,
            )
            new_video_comment_reaction = await self._video_comment_reaction_service.create(
                video_comment_reaction=video_comment_reaction_entity
            )
            return new_video_comment_reaction, True
