from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.posts.commands import DeletePostCommand
from app.domain.channels.services import IChannelService
from app.domain.posts.services import IPostService


@dataclass
class DeletePostUseCase:
    channel_service: IChannelService
    post_service: IPostService
    transaction_manager: ITransactionManager

    async def execute(self, command: DeletePostCommand) -> None:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            post = await self.post_service.try_get_by_id(id=command.post_id)
            self.post_service.ensure_post_access(post=post, channel=channel)
            await self.post_service.try_delete_by_id(id=post.id)
