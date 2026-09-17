from dataclasses import dataclass
from pathlib import Path

from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import ConfirmVideoThumbnailUploadCommand
from app.core.configs import settings
from app.domain.channels.service import IChannelService
from app.domain.common.constants import IMAGE_FILE_MIME_TYPES
from app.domain.common.exceptions.s3 import S3ObjectAccessForbiddenError
from app.domain.videos.constants import VIDEO_THUMBNAIL_MAX_SIZE
from app.domain.videos.exceptions import (
    VideoThumbnailAlreadySetError,
    VideoThumbnailInvalidContentTypeError,
    VideoThumbnailInvalidKeyError,
    VideoThumbnailSizeTooBigError,
    VideoThumbnailVideoIdMismatchError,
)
from app.domain.videos.service import IVideoService


@dataclass
class ConfirmVideoThumbnailUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_service: IS3Service
    _file_type_detector: IFileTypeDetector
    _transaction_manager: ITransactionManager

    async def execute(self, command: ConfirmVideoThumbnailUploadCommand) -> None:
        key = Path(command.key)
        if (
            key.suffix.lower() not in IMAGE_FILE_MIME_TYPES
            or str(key.parent) != settings.s3_tmp_video_thumbnails_key_prefix
        ):
            raise VideoThumbnailInvalidKeyError(key=command.key)

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)

        thumbnail_s3_key = f'{settings.s3_video_thumbnails_key_prefix}/{key.name}'

        if video.thumbnail_s3_key == thumbnail_s3_key:
            raise VideoThumbnailAlreadySetError(video_id=video.id, thumbnail_s3_key=thumbnail_s3_key)

        thumbnail_object = await self._s3_service.get_object(
            bucket=settings.s3_public_bucket_name,
            key=command.key,
            range='bytes=0-2047',
        )

        thumbnail_metadata_channel_id = thumbnail_object['Metadata'].get('channel_id')
        if thumbnail_metadata_channel_id != str(channel.id):
            raise S3ObjectAccessForbiddenError(channel_id=channel.id, key=command.key)

        thumbnail_metadata_video_id = thumbnail_object['Metadata'].get('video_id')
        if thumbnail_metadata_video_id != video.id:
            raise VideoThumbnailVideoIdMismatchError(
                video_id=video.id,
                metadata_video_id=thumbnail_metadata_video_id,
                thumbnail_s3_key=command.key,
            )

        _, thumbnail_metadata_content_length = thumbnail_object['ContentRange'].split('/')
        thumbnail_metadata_content_length = int(thumbnail_metadata_content_length)
        if thumbnail_metadata_content_length > VIDEO_THUMBNAIL_MAX_SIZE:
            await self._s3_service.schedule_delete_object(bucket=settings.s3_public_bucket_name, key=command.key)
            raise VideoThumbnailSizeTooBigError(
                key=command.key,
                file_size=thumbnail_metadata_content_length,
                file_max_size=VIDEO_THUMBNAIL_MAX_SIZE,
            )

        thumbnail_object_data = await thumbnail_object['Body'].read()
        thumbnail_actual_mime_type = self._file_type_detector.detect(content=thumbnail_object_data)
        thumbnail_metadata_mime_type: str = thumbnail_object['ContentType']

        if (
            thumbnail_metadata_mime_type not in IMAGE_FILE_MIME_TYPES.values()
            or thumbnail_actual_mime_type not in IMAGE_FILE_MIME_TYPES.values()
        ):
            await self._s3_service.schedule_delete_object(bucket=settings.s3_public_bucket_name, key=command.key)
            raise VideoThumbnailInvalidContentTypeError(
                key=command.key,
                metadata_content_type=thumbnail_metadata_mime_type,
                actual_content_type=thumbnail_actual_mime_type,
            )

        await self._s3_service.copy_object(
            bucket=settings.s3_public_bucket_name,
            current_key=command.key,
            new_key=thumbnail_s3_key,
        )
        await self._s3_service.schedule_delete_object(
            bucket=settings.s3_public_bucket_name,
            key=command.key,
        )

        old_thumbnail_s3_key = video.thumbnail_s3_key

        video.set_thumbnail_s3_key(value=thumbnail_s3_key)
        async with self._transaction_manager:
            await self._video_service.try_update(video=video)

        if old_thumbnail_s3_key is not None and video.thumbnail_s3_key != old_thumbnail_s3_key:
            await self._s3_service.schedule_delete_object(
                bucket=settings.s3_public_bucket_name,
                key=old_thumbnail_s3_key,
            )
