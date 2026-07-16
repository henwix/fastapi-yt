from dataclasses import dataclass

from app.application.channels.commands import ConfirmChannelAvatarUploadCommand
from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.enums import ChannelAvatarFileContentTypesEnum
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidFileContentTypeError,
)
from app.domain.channels.services import IChannelService
from app.domain.common.exceptions import S3ObjectAccessForbiddenError


@dataclass
class ConfirmChannelAvatarUploadUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager
    _s3_provider: IS3Provider
    _task_queue: ITaskQueue

    async def execute(self, command: ConfirmChannelAvatarUploadCommand) -> None:
        self._channel_service.validate_channel_avatar_file_format_and_get_content_type(value=command.key)
        self._channel_service.validate_channel_avatar_key(key=command.key, key_prefix=settings.s3_avatars_key_prefix)

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        if channel.avatar_s3_key is not None and channel.avatar_s3_key == command.key:
            raise ChannelAvatarAlreadySetError(channel_id=channel.id, avatar_s3_key=channel.avatar_s3_key)

        avatar_info = await self._s3_provider.head_object(bucket=settings.s3_public_bucket_name, key=command.key)
        avatar_metadata_channel_id = avatar_info['Metadata'].get('channel_id')
        avatar_metadata_content_type = avatar_info['ContentType']

        if avatar_metadata_channel_id != str(channel.id):
            raise S3ObjectAccessForbiddenError(channel_id=channel.id, key=command.key)

        if avatar_metadata_content_type not in ChannelAvatarFileContentTypesEnum:
            await self._task_queue.delete_s3_object(bucket=settings.s3_public_bucket_name, key=command.key)
            raise ChannelAvatarInvalidFileContentTypeError(key=command.key, content_type=avatar_metadata_content_type)

        old_channel_avatar_s3_key = channel.avatar_s3_key

        channel.set_avatar_s3_key(key=command.key)
        async with self._transaction_manager:
            await self._channel_service.try_update(channel=channel)

        if old_channel_avatar_s3_key is not None:
            await self._task_queue.delete_s3_object(
                bucket=settings.s3_public_bucket_name,
                key=old_channel_avatar_s3_key,
            )
