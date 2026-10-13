from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.posts.commands.posts import UpdatePostCommand
from app.domain.channels.services import IChannelService
from app.domain.posts.entities import Post
from app.domain.posts.services import IPostService


@dataclass
class UpdatePostUseCase:
    _channel_service: IChannelService
    _post_service: IPostService
    _tm: ITransactionManager

    async def execute(self, command: UpdatePostCommand) -> Post:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)

            post = await self._post_service.try_get_existing_by_id(id=command.post_id)
            self._post_service.ensure_post_access(post=post, channel=channel)

            post.set_text(value=command.text)
            return await self._post_service.try_update(post=post)
