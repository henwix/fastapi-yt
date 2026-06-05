from dataclasses import dataclass

from app.application.commands.posts import UpdatePostCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class UpdatePostUseCase:
    channel_service: IChannelService
    post_service: IPostService
    transaction_manager: ITransactionManager

    async def execute(self, command: UpdatePostCommand) -> Post:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.channel_id)
            post = await self.post_service.try_get_by_id(id=command.post_id)
            self.post_service.ensure_post_access(post=post, channel=channel)
            post.update(text=command.text)
            return await self.post_service.try_update(post=post)
