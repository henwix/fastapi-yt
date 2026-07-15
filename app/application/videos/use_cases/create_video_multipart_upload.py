from dataclasses import dataclass

from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CreateVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.videos.entities import Video
from app.domain.videos.services import IVideoService


@dataclass
class CreateVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_provider: IS3Provider
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoMultipartUploadCommand) -> Video:
        content_type = self._video_service.validate_video_file_format_and_get_content_type(value=command.filename)

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        upload_id, key = await self._s3_provider.create_multipart_upload(
            bucket=settings.s3_private_bucket_name,
            filename=command.filename,
            content_type=content_type,
            key_prefix=settings.s3_videos_key_prefix,
            metadata={'channel_id': str(channel.id)},
        )
        video = Video.create(
            channel_id=channel.id,
            title=command.title,
            description=command.description,
            privacy_status=command.privacy_status,
            upload_id=upload_id,
            s3_key=key,
        )

        async with self._transaction_manager:
            return await self._video_service.create(video=video)
