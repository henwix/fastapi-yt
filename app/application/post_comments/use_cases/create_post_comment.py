from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comments.commands import CreatePostCommentCommand
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.services import IPostCommentService
from app.domain.posts.services import IPostService


@dataclass
class CreatePostCommentUseCase:
    _channel_service: IChannelService
    _post_service: IPostService
    _post_comment_service: IPostCommentService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreatePostCommentCommand) -> PostComment:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        post = await self._post_service.try_get_by_id(id=command.post_id)

        reply_comment = None
        if command.reply_comment_id is not Empty.UNSET:
            reply_comment = await self._post_comment_service.try_get_by_id_and_post_id(
                id=command.reply_comment_id,
                post_id=post.id,
            )

        comment_entity = PostComment.create(
            post_id=post.id,
            channel_id=channel.id,
            reply_comment_id=reply_comment.id if reply_comment else None,
            text=command.text,
        )

        async with self._transaction_manager:
            return await self._post_comment_service.create(post_comment=comment_entity)
