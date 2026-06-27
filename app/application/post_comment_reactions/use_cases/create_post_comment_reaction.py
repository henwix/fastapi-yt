from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comment_reactions.commands import CreatePostCommentReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.post_comment_reactions.entities import PostCommentReaction
from app.domain.post_comment_reactions.services import IPostCommentReactionService
from app.domain.post_comments.services import IPostCommentService


@dataclass
class CreatePostCommentReactionUseCase:
    channel_service: IChannelService
    post_comment_service: IPostCommentService
    post_comment_reaction_service: IPostCommentReactionService
    transaction_manager: ITransactionManager

    async def execute(self, command: CreatePostCommentReactionCommand) -> tuple[PostCommentReaction, bool]:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            post_comment = await self.post_comment_service.try_get_by_id(id=command.post_comment_id)
            post_comment_reaction = await self.post_comment_reaction_service.get_by_post_comment_id_and_channel_id(
                post_comment_id=post_comment.id, channel_id=channel.id
            )

            if post_comment_reaction is not None:
                if post_comment_reaction.reaction_type != command.reaction_type:
                    post_comment_reaction.set_reaction_type(reaction_type=command.reaction_type)
                    post_comment_reaction = await self.post_comment_reaction_service.try_update(
                        post_comment_reaction=post_comment_reaction
                    )
                return post_comment_reaction, False

            post_comment_reaction_entity = PostCommentReaction.create(
                post_comment_id=post_comment.id,
                channel_id=channel.id,
                reaction_type=command.reaction_type,
            )
            new_post_comment_reaction = await self.post_comment_reaction_service.create(
                post_comment_reaction=post_comment_reaction_entity
            )
            return new_post_comment_reaction, True
