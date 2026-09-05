from dataclasses import dataclass

from app.application.channels.commands import DeleteChannelAvatarCommand
from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelAvatarNotFoundError
from app.domain.channels.service import IChannelService


@dataclass
class DeleteChannelAvatarUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager
    _s3_service: IS3Service

    async def execute(self, command: DeleteChannelAvatarCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        if channel.avatar_s3_key is None:
            raise ChannelAvatarNotFoundError(channel_id=channel.id)

        channel_avatar_s3_key = channel.avatar_s3_key

        channel.set_avatar_s3_key(value=None)
        async with self._transaction_manager:
            await self._channel_service.try_update(channel=channel)

        await self._s3_service.schedule_delete_object(bucket=settings.s3_public_bucket_name, key=channel_avatar_s3_key)
