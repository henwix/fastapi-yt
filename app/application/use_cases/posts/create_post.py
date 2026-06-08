from dataclasses import dataclass

from app.application.commands.posts import CreatePostCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class CreatePostUseCase:
    channel_service: IChannelService
    post_service: IPostService
    transaction_manager: ITransactionManager

    async def execute(self, command: CreatePostCommand) -> Post:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            post_entity = Post.create(text=command.text, channel_id=channel.id)
            return await self.post_service.create(post=post_entity)
