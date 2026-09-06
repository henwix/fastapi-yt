from dataclasses import dataclass
from pathlib import Path

from app.application.channels.commands import ConfirmChannelAvatarUploadCommand
from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.constants import CHANNEL_AVATAR_FILE_MIME_TYPES, CHANNEL_AVATAR_MAX_SIZE
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidFileContentTypeError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarSizeTooBigError,
)
from app.domain.channels.service import IChannelService
from app.domain.common.exceptions import S3ObjectAccessForbiddenError


@dataclass
class ConfirmChannelAvatarUploadUseCase:
    _channel_service: IChannelService
    _s3_service: IS3Service
    _file_type_detector: IFileTypeDetector
    _transaction_manager: ITransactionManager

    async def execute(self, command: ConfirmChannelAvatarUploadCommand) -> None:
        self._channel_service.validate_channel_avatar_file_format_and_get_content_type(value=command.key)
        if not command.key.startswith(settings.s3_tmp_avatars_key_prefix):
            raise ChannelAvatarInvalidKeyError(key=command.key)

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        avatar_s3_key = f'{settings.s3_avatars_key_prefix}/{Path(command.key).name}'

        if channel.avatar_s3_key is not None and channel.avatar_s3_key == avatar_s3_key:
            raise ChannelAvatarAlreadySetError(channel_id=channel.id, avatar_s3_key=channel.avatar_s3_key)

        avatar_object = await self._s3_service.get_object(
            bucket=settings.s3_public_bucket_name,
            key=command.key,
            range='bytes=0-2047',
        )
        avatar_metadata_channel_id: str = avatar_object['Metadata'].get('channel_id')
        avatar_metadata_mime_type: str = avatar_object['ContentType']
        avatar_metadata_content_length: int = avatar_object['ContentLength']

        if avatar_metadata_channel_id != str(channel.id):
            raise S3ObjectAccessForbiddenError(channel_id=channel.id, key=command.key)

        if avatar_metadata_content_length > CHANNEL_AVATAR_MAX_SIZE:
            await self._s3_service.schedule_delete_object(bucket=settings.s3_public_bucket_name, key=command.key)
            raise ChannelAvatarSizeTooBigError(
                key=command.key,
                file_size=avatar_metadata_content_length,
                file_max_size=CHANNEL_AVATAR_MAX_SIZE,
            )

        avatar_object_data = await avatar_object['Body'].read()
        actual_avatar_mime_type = self._file_type_detector.detect(content=avatar_object_data)

        if (
            actual_avatar_mime_type not in CHANNEL_AVATAR_FILE_MIME_TYPES.values()
            or avatar_metadata_mime_type not in CHANNEL_AVATAR_FILE_MIME_TYPES.values()
        ):
            await self._s3_service.schedule_delete_object(bucket=settings.s3_public_bucket_name, key=command.key)
            raise ChannelAvatarInvalidFileContentTypeError(
                key=command.key,
                metadata_content_type=avatar_metadata_mime_type,
                actual_content_type=actual_avatar_mime_type,
            )

        await self._s3_service.copy_object(
            bucket=settings.s3_public_bucket_name,
            current_key=command.key,
            new_key=avatar_s3_key,
        )
        await self._s3_service.schedule_delete_object(
            bucket=settings.s3_public_bucket_name,
            key=command.key,
        )

        old_channel_avatar_s3_key = channel.avatar_s3_key

        channel.set_avatar_s3_key(value=avatar_s3_key)
        async with self._transaction_manager:
            await self._channel_service.try_update(channel=channel)

        if old_channel_avatar_s3_key is not None and channel.avatar_s3_key != old_channel_avatar_s3_key:
            await self._s3_service.schedule_delete_object(
                bucket=settings.s3_public_bucket_name,
                key=old_channel_avatar_s3_key,
            )
