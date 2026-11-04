from dataclasses import dataclass
from pathlib import Path

from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CompleteVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.common.constants import VIDEO_FILE_MIME_TYPES
from app.domain.files.entities import File
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.entities import Video
from app.domain.videos.exceptions import (
    VideoInvalidContentTypeError,
    VideoSizeTooSmallError,
    VideoUploadFailedToCompleteError,
    VideoUploadNotCreatedError,
)
from app.domain.videos.services import IVideoService


@dataclass
class CompleteVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _s3_service: IS3Service
    _file_type_detector: IFileTypeDetector
    _tm: ITransactionManager

    async def execute(self, command: CompleteVideoMultipartUploadCommand) -> None:
        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)
        self._video_service.ensure_video_upload_created(video=video)

        video_file = await self._file_service.get_by_id(id=video.video_file_id)
        if not video_file:
            raise VideoUploadNotCreatedError(video_id=video.id)

        await self._s3_service.complete_multipart_upload(
            bucket=video_file.bucket,
            key=video_file.key,
            upload_id=video.video_upload_id,
            parts=command.parts,
        )

        video_head_object = await self._s3_service.head_object(
            key=video_file.key,
            bucket=video_file.bucket,
        )
        video_content_length = video_head_object['ContentLength']
        if video_content_length == 0:
            await self._delete_video_file(video=video, video_file=video_file)
            raise VideoSizeTooSmallError(
                key=video_file.key,
                bucket=settings.s3_private_bucket_name,
                file_size=video_content_length,
            )

        video_object = await self._s3_service.get_object(
            bucket=video_file.bucket,
            key=video_file.key,
            range='bytes=0-2047',
        )
        video_object_data = await video_object['Body'].read()

        video_metadata_mime_type: str = video_object['ContentType']
        video_actual_mime_type = self._file_type_detector.detect(content=video_object_data)
        allowed_mime_types = VIDEO_FILE_MIME_TYPES.get(Path(video_file.key).suffix.lower(), [])

        if video_metadata_mime_type not in allowed_mime_types or video_actual_mime_type not in allowed_mime_types:
            await self._delete_video_file(video=video, video_file=video_file)
            raise VideoInvalidContentTypeError(
                key=video_file.key,
                metadata_content_type=video_metadata_mime_type,
                actual_content_type=video_actual_mime_type,
            )

        is_video_updated = await self._video_service.update_upload_completed(
            id=video.id,
            video_upload_id=video.video_upload_id,
            video_file_id=video_file.id,
        )
        if not is_video_updated:
            raise VideoUploadFailedToCompleteError(
                video_id=video.id,
                key=video_file.key,
                bucket=video_file.bucket,
                error_detail='video_not_updated_after_successful_validation',
            )

    async def _delete_video_file(self, video: Video, video_file: File) -> None:
        async with self._tm.begin(commit=True):
            is_video_updated = await self._video_service.update_upload_canceled(
                id=video.id,
                video_upload_id=video.video_upload_id,
                video_file_id=video_file.id,
            )
            if not is_video_updated:
                raise VideoUploadFailedToCompleteError(
                    video_id=video.id,
                    key=video_file.key,
                    bucket=video_file.bucket,
                    error_detail='video_not_updated_if_file_invalid',
                )

            is_video_file_deleted = await self._file_service.delete_by_id(id=video_file.id)
            if is_video_file_deleted:
                video_file_cleanup = FileCleanup.create(s3_key=video_file.key, bucket=video_file.bucket)
                await self._file_cleanup_service.upsert(cleanup=video_file_cleanup)
