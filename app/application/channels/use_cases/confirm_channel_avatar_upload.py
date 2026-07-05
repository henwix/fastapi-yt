from dataclasses import dataclass

from app.application.channels.commands import ConfirmChannelAvatarUploadCommand
from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.common.exceptions import S3FileAccessForbiddenError


@dataclass
class ChannelAvatarUploadConfirmUseCase:
    channel_service: IChannelService
    transaction_manager: ITransactionManager
    s3_provider: IS3Provider

    async def execute(self, command: ConfirmChannelAvatarUploadCommand) -> None:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)

            avatar_info = await self.s3_provider.head_object(bucket=settings.s3_public_bucket_name, key=command.key)
            avatar_metadata_channel_id = avatar_info['Metadata'].get('channel_id')

            if avatar_metadata_channel_id != str(channel.id):
                raise S3FileAccessForbiddenError(channel_id=channel.id, key=command.key)

            if channel.avatar_s3_key != command.key:
                channel.set_avatar_s3_key(key=command.key)
                await self.channel_service.try_update(channel=channel)
