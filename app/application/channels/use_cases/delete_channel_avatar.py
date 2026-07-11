from dataclasses import dataclass

from app.application.channels.commands import DeleteChannelAvatarCommand
from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelAvatarNotFoundError
from app.domain.channels.services import IChannelService


@dataclass
class DeleteChannelAvatarUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager
    _task_queue: ITaskQueue

    async def execute(self, command: DeleteChannelAvatarCommand) -> None:
        async with self._transaction_manager:
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
            if channel.avatar_s3_key is None:
                raise ChannelAvatarNotFoundError(channel_id=channel.id)
            await self._task_queue.delete_s3_object(bucket=settings.s3_public_bucket_name, key=channel.avatar_s3_key)
            channel.set_avatar_s3_key(key=None)
            await self._channel_service.try_update(channel=channel)
