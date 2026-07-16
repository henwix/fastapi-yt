from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.posts.commands import UpdatePostCommand
from app.domain.channels.services import IChannelService
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class UpdatePostUseCase:
    _channel_service: IChannelService
    _post_service: IPostService
    _transaction_manager: ITransactionManager

    async def execute(self, command: UpdatePostCommand) -> Post:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        post = await self._post_service.try_get_by_id(id=command.post_id)
        self._post_service.ensure_post_access(post=post, channel=channel)

        post.update(text=command.text)
        async with self._transaction_manager:
            return await self._post_service.try_update(post=post)
