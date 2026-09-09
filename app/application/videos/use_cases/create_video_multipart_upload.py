from dataclasses import dataclass

from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CreateVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.service import IChannelService
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoUploadAlreadyCreatedError
from app.domain.videos.service import IVideoService


@dataclass
class CreateVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_service: IS3Service
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoMultipartUploadCommand) -> None:
        content_type = self._video_service.validate_video_file_format_and_get_content_type(value=command.filename)
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        if video.upload_status is VideoUploadStatusEnum.UPLOADING:
            raise VideoUploadAlreadyCreatedError(video_id=video.id)

        upload_id, key = await self._s3_service.create_multipart_upload(
            bucket=settings.s3_private_bucket_name,
            filename=command.filename,
            content_type=content_type,
            key_prefix=settings.s3_videos_key_prefix,
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
