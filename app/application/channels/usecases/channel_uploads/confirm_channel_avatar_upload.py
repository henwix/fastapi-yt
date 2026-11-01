from dataclasses import dataclass
from pathlib import Path

from app.application.channels.commands import ConfirmChannelAvatarUploadCommand
from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.channels.constants import CHANNEL_AVATAR_MAX_SIZE
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidContentTypeError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarSizeTooBigError,
    ChannelAvatarSizeTooSmallError,
    ChannelAvatarUploadConfirmationFailedError,
)
from app.domain.channels.services import IChannelService
from app.domain.common.constants import IMAGE_FILE_MIME_TYPES
from app.domain.common.exceptions.s3 import S3ObjectAccessForbiddenError
from app.domain.common.repos.kv import IKVRepo
from app.domain.files.entities import File
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService


@dataclass
class ConfirmChannelAvatarUploadUseCase:
    _channel_service: IChannelService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _s3_service: IS3Service
    _kv_repo: IKVRepo
    _tm: ITransactionManager
    _file_type_detector: IFileTypeDetector

    async def execute(self, command: ConfirmChannelAvatarUploadCommand) -> None:
        key = Path(command.key)
        if (
            key.suffix.lower() not in IMAGE_FILE_MIME_TYPES
            or str(key.parent) != settings.s3_tmp_channel_avatars_key_prefix
        ):
            raise ChannelAvatarInvalidKeyError(key=command.key, error_detail='invalid_provided_key')

        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        current_avatar_file = None
        if channel.avatar_file_id is not None:
            current_avatar_file = await self._file_service.get_by_id(id=channel.avatar_file_id)

        avatar_key = f'{settings.s3_channel_avatars_key_prefix}/{key.name}'
        bucket_name = settings.s3_public_bucket_name

        if (
            current_avatar_file is not None
            and current_avatar_file.key == avatar_key
            and current_avatar_file.bucket == bucket_name
        ):
            raise ChannelAvatarAlreadySetError(
                channel_id=channel.id,
                avatar_key=current_avatar_file.key,
                avatar_bucket=current_avatar_file.bucket,
            )

        is_avatar_key_deleted = await self._kv_repo.delete_with_lock(
            key=f'set_channel_avatar_url:{channel.id}:{bucket_name}:{command.key}',
        )
        if not is_avatar_key_deleted:
            raise ChannelAvatarInvalidKeyError(key=command.key, error_detail='upload_url_expired_or_deleted')

        avatar_head_object = await self._s3_service.head_object(
            key=command.key,
            bucket=bucket_name,
        )

        avatar_metadata_channel_id = avatar_head_object['Metadata'].get('channel_id')
        if avatar_metadata_channel_id != str(channel.id):
            raise S3ObjectAccessForbiddenError(channel_id=channel.id, key=command.key)

        avatar_metadata_content_length = avatar_head_object['ContentLength']
        if avatar_metadata_content_length == 0:
            await self._create_cleanup(key=command.key, bucket=bucket_name)
            raise ChannelAvatarSizeTooSmallError(
                key=command.key,
                bucket=bucket_name,
                file_size=avatar_metadata_content_length,
            )
        if avatar_metadata_content_length > CHANNEL_AVATAR_MAX_SIZE:
            await self._create_cleanup(key=command.key, bucket=bucket_name)
            raise ChannelAvatarSizeTooBigError(
                key=command.key,
                bucket=bucket_name,
                file_size=avatar_metadata_content_length,
                file_max_size=CHANNEL_AVATAR_MAX_SIZE,
            )

        avatar_object = await self._s3_service.get_object(
            bucket=bucket_name,
            key=command.key,
            range='bytes=0-2047',
        )
        avatar_object_data = await avatar_object['Body'].read()
        actual_avatar_mime_type = self._file_type_detector.detect(content=avatar_object_data)
        avatar_metadata_mime_type: str = avatar_object['ContentType']

        if (
            actual_avatar_mime_type not in IMAGE_FILE_MIME_TYPES.values()
            or avatar_metadata_mime_type not in IMAGE_FILE_MIME_TYPES.values()
        ):
            await self._create_cleanup(key=command.key, bucket=bucket_name)
            raise ChannelAvatarInvalidContentTypeError(
                key=command.key,
                metadata_content_type=avatar_metadata_mime_type,
                actual_content_type=actual_avatar_mime_type,
            )

        await self._s3_service.copy_object(
            bucket=bucket_name,
            current_key=command.key,
            new_key=avatar_key,
        )
        await self._create_cleanup(key=command.key, bucket=bucket_name)

        async with self._tm.begin(commit=True):
            new_avatar_file = await self._file_service.create(
                file=File.create(key=avatar_key, bucket=bucket_name),
            )
            is_new_avatar_file_set = await self._channel_service.update_avatar_file_id(
                id=channel.id,
                new_avatar_file_id=new_avatar_file.id,
                prev_avatar_file_id=channel.avatar_file_id,
            )
            if not is_new_avatar_file_set:
                await self._tm.rollback(with_exc=True)
            if current_avatar_file is not None:
                is_current_avatar_file_deleted = await self._file_service.delete_by_id(id=current_avatar_file.id)
                if is_current_avatar_file_deleted:
                    await self._create_cleanup(key=current_avatar_file.key, bucket=current_avatar_file.bucket)

        if not is_new_avatar_file_set:
            await self._create_cleanup(key=avatar_key, bucket=bucket_name)
            raise ChannelAvatarUploadConfirmationFailedError(
                channel_id=channel.id,
                avatar_key=avatar_key,
                avatar_bucket=bucket_name,
                error_detail='concurrent_modification_error',
            )

    async def _create_cleanup(self, key: str, bucket: str) -> None:
        file_cleanup = FileCleanup.create(s3_key=key, bucket=bucket)
        await self._file_cleanup_service.upsert(cleanup=file_cleanup)
