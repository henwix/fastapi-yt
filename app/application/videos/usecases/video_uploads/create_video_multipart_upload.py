from dataclasses import dataclass
from pathlib import Path

from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CreateVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.common.constants import VIDEO_FILE_MIME_TYPES
from app.domain.files.entities import File
from app.domain.files.services import IFileService
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoInvalidFilenameError,
    VideoUploadAlreadyCreatedError,
    VideoUploadFailedToCreateError,
)
from app.domain.videos.services import IVideoService


@dataclass
class CreateVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _file_service: IFileService
    _s3_service: IS3Service
    _tm: ITransactionManager

    async def execute(self, command: CreateVideoMultipartUploadCommand) -> None:
        filename_extension = Path(command.filename).suffix.lower()
        if filename_extension not in VIDEO_FILE_MIME_TYPES:
            raise VideoInvalidFilenameError(filename=command.filename)
        content_type = VIDEO_FILE_MIME_TYPES[filename_extension][0]

        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        if video.video_upload_status is VideoUploadStatusEnum.UPLOADING:
            raise VideoUploadAlreadyCreatedError(video_id=video.id)

        key = self._s3_service.generate_unique_bucket_key(
            filename=command.filename, key_prefix=settings.s3_videos_key_prefix
        )
        bucket_name = settings.s3_private_bucket_name
        upload_id = await self._s3_service.create_multipart_upload(
            bucket=bucket_name,
            key=key,
            content_type=content_type,
            metadata={
                'channel_id': str(channel.id),
                'video_id': video.id,
            },
        )

        async with self._tm.begin(commit=True):
            video_file = await self._file_service.create(file=File.create(key=key, bucket=bucket_name))
            is_video_updated = await self._video_service.update_upload_created(
                id=video.id,
                video_upload_id=upload_id,
                video_file_id=video_file.id,
            )
            if not is_video_updated:
                await self._tm.rollback()

        if not is_video_updated:
            await self._s3_service.schedule_abort_multipart_upload(
                bucket=bucket_name,
                key=key,
                upload_id=upload_id,
            )
            raise VideoUploadFailedToCreateError(video_id=video.id, key=key, bucket=bucket_name)
