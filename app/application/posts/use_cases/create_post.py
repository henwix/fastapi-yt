from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.posts.commands import CreatePostCommand
from app.domain.channels.services import IChannelService
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class CreatePostUseCase:
    _channel_service: IChannelService
    _post_service: IPostService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreatePostCommand) -> Post:
        async with self._transaction_manager:
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
            post_entity = Post.create(text=command.text, channel_id=channel.id)
            return await self._post_service.create(post=post_entity)
