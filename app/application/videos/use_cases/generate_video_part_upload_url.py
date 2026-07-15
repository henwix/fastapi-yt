from dataclasses import dataclass

from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.videos.commands import GenerateVideoPartUploadUrlCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.videos.exceptions import VideoInvalidKeyError
from app.domain.videos.services import IVideoService


@dataclass
class GenerateVideoPartUploadUrlUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_provider: IS3Provider

    async def execute(self, command: GenerateVideoPartUploadUrlCommand) -> str:
        self._video_service.validate_video_file_format_and_get_content_type(value=command.key)
        if not command.key.startswith(settings.s3_videos_key_prefix):
            raise VideoInvalidKeyError(key=command.key)

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_upload_id_and_s3_key(
            upload_id=command.upload_id,
            s3_key=command.key,
        )

        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        return await self._s3_provider.generate_part_upload_url(
            bucket=settings.s3_private_bucket_name,
            key=command.key,
            upload_id=command.upload_id,
            part_number=command.part_number,
            expires_in=120,
        )
