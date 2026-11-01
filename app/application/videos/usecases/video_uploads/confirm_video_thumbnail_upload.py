from dataclasses import dataclass
from pathlib import Path

from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import ConfirmVideoThumbnailUploadCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.common.constants import IMAGE_FILE_MIME_TYPES
from app.domain.common.exceptions.s3 import S3ObjectAccessForbiddenError
from app.domain.common.repos.kv import IKVRepo
from app.domain.files.entities import File
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.constants import VIDEO_THUMBNAIL_MAX_SIZE
from app.domain.videos.exceptions import (
    VideoThumbnailAlreadySetError,
    VideoThumbnailInvalidContentTypeError,
    VideoThumbnailInvalidKeyError,
    VideoThumbnailSizeTooBigError,
    VideoThumbnailSizeTooSmallError,
    VideoThumbnailUploadConfirmationFailedError,
    VideoThumbnailVideoIdMismatchError,
)
from app.domain.videos.services import IVideoService


@dataclass
class ConfirmVideoThumbnailUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _s3_service: IS3Service
    _kv_repo: IKVRepo
    _tm: ITransactionManager
    _file_type_detector: IFileTypeDetector

    async def execute(self, command: ConfirmVideoThumbnailUploadCommand) -> None:
        key = Path(command.key)
        if (
            key.suffix.lower() not in IMAGE_FILE_MIME_TYPES
            or str(key.parent) != settings.s3_tmp_video_thumbnails_key_prefix
        ):
            raise VideoThumbnailInvalidKeyError(key=command.key, error_detail='invalid_provided_key')

        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)
        current_video_thumbnail_file = None
        if video.thumbnail_file_id is not None:
            current_video_thumbnail_file = await self._file_service.get_by_id(id=video.thumbnail_file_id)

        thumbnail_key = f'{settings.s3_video_thumbnails_key_prefix}/{key.name}'
        bucket_name = settings.s3_public_bucket_name

        if (
            current_video_thumbnail_file is not None
            and current_video_thumbnail_file.key == thumbnail_key
            and current_video_thumbnail_file.bucket == bucket_name
        ):
            raise VideoThumbnailAlreadySetError(video_id=video.id, thumbnail_s3_key=thumbnail_key)

        is_video_thumbnail_key_deleted = await self._kv_repo.delete_with_lock(
            key=f'set_video_thumbnail:{video.id}:{bucket_name}:{command.key}'
        )
        if not is_video_thumbnail_key_deleted:
            raise VideoThumbnailInvalidKeyError(key=command.key, error_detail='upload_url_expired_or_deleted')

        thumbnail_head_object = await self._s3_service.head_object(
            bucket=bucket_name,
            key=command.key,
        )

        thumbnail_metadata_channel_id = thumbnail_head_object['Metadata'].get('channel_id')
        if thumbnail_metadata_channel_id != str(channel.id):
            raise S3ObjectAccessForbiddenError(channel_id=channel.id, key=command.key)

        thumbnail_metadata_video_id = thumbnail_head_object['Metadata'].get('video_id')
        if thumbnail_metadata_video_id != video.id:
            raise VideoThumbnailVideoIdMismatchError(
                video_id=video.id,
                metadata_video_id=thumbnail_metadata_video_id,
                thumbnail_s3_key=command.key,
            )

        thumbnail_metadata_content_length = thumbnail_head_object['ContentLength']
        if thumbnail_metadata_content_length == 0:
            await self._create_cleanup(key=command.key, bucket=bucket_name)
            raise VideoThumbnailSizeTooSmallError(
                key=command.key,
                bucket=bucket_name,
                file_size=thumbnail_metadata_content_length,
            )
        if thumbnail_metadata_content_length > VIDEO_THUMBNAIL_MAX_SIZE:
            await self._create_cleanup(key=command.key, bucket=bucket_name)
            raise VideoThumbnailSizeTooBigError(
                key=command.key,
                bucket=bucket_name,
                file_size=thumbnail_metadata_content_length,
                file_max_size=VIDEO_THUMBNAIL_MAX_SIZE,
            )

        thumbnail_object = await self._s3_service.get_object(
            bucket=bucket_name,
            key=command.key,
            range='bytes=0-2047',
        )
        thumbnail_object_data = await thumbnail_object['Body'].read()
        thumbnail_actual_mime_type = self._file_type_detector.detect(content=thumbnail_object_data)
        thumbnail_metadata_mime_type: str = thumbnail_object['ContentType']

        if (
            thumbnail_metadata_mime_type not in IMAGE_FILE_MIME_TYPES.values()
            or thumbnail_actual_mime_type not in IMAGE_FILE_MIME_TYPES.values()
        ):
            await self._create_cleanup(key=command.key, bucket=bucket_name)
            raise VideoThumbnailInvalidContentTypeError(
                key=command.key,
                metadata_content_type=thumbnail_metadata_mime_type,
                actual_content_type=thumbnail_actual_mime_type,
            )

        await self._s3_service.copy_object(
            bucket=bucket_name,
            current_key=command.key,
            new_key=thumbnail_key,
        )
        await self._create_cleanup(key=command.key, bucket=bucket_name)

        async with self._tm.begin(commit=True):
            new_thumbnail_file = await self._file_service.create(
                file=File.create(key=thumbnail_key, bucket=bucket_name)
            )
            is_new_thumbnail_file_set = await self._video_service.update_thumbnail_file_id(
                id=video.id,
                new_thumbnail_file_id=new_thumbnail_file.id,
                prev_thumbnail_file_id=video.thumbnail_file_id,
            )
            if not is_new_thumbnail_file_set:
                await self._tm.rollback(with_exc=True)
            if current_video_thumbnail_file is not None:
                is_video_thumbnail_file_deleted = await self._file_service.delete_by_id(
                    id=current_video_thumbnail_file.id,
                )
                if is_video_thumbnail_file_deleted:
                    await self._create_cleanup(
                        key=current_video_thumbnail_file.key,
                        bucket=current_video_thumbnail_file.bucket,
                    )
        if not is_new_thumbnail_file_set:
            await self._create_cleanup(key=thumbnail_key, bucket=bucket_name)
            raise VideoThumbnailUploadConfirmationFailedError(
                video_id=video.id,
                key=thumbnail_key,
                bucket=bucket_name,
                error_detail='concurrent_modification_error',
            )

    async def _create_cleanup(self, key: str, bucket: str) -> None:
        file_cleanup = FileCleanup.create(s3_key=key, bucket=bucket)
        await self._file_cleanup_service.upsert(cleanup=file_cleanup)
