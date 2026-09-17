from dataclasses import dataclass
from pathlib import Path

from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CreateVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.service import IChannelService
from app.domain.common.constants import VIDEO_FILE_MIME_TYPES
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoInvalidFilenameError, VideoUploadAlreadyCreatedError
from app.domain.videos.service import IVideoService


@dataclass
class CreateVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_service: IS3Service
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoMultipartUploadCommand) -> None:
        filename_extension = Path(command.filename).suffix.lower()
        if filename_extension not in VIDEO_FILE_MIME_TYPES:
            raise VideoInvalidFilenameError(filename=command.filename)
        content_type = VIDEO_FILE_MIME_TYPES[filename_extension][0]

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        if video.upload_status is VideoUploadStatusEnum.UPLOADING:
            raise VideoUploadAlreadyCreatedError(video_id=video.id)

        key = self._s3_service.generate_unique_bucket_key(
            filename=command.filename, key_prefix=settings.s3_videos_key_prefix
        )
        upload_id = await self._s3_service.create_multipart_upload(
            bucket=settings.s3_private_bucket_name,
            key=key,
            content_type=content_type,
            metadata={
                'channel_id': str(channel.id),
                'video_id': video.id,
            },
        )

        video.set_upload_id(value=upload_id)
        video.set_s3_key(value=key)
        video.set_upload_status(value=VideoUploadStatusEnum.UPLOADING)

        async with self._transaction_manager:
            await self._video_service.try_update(video=video)
