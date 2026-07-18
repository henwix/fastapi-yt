from dataclasses import dataclass

from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.videos.commands import GenerateVideoPartUploadUrlCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.videos.services import IVideoService


@dataclass
class GenerateVideoPartUploadUrlUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_provider: IS3Provider

    async def execute(self, command: GenerateVideoPartUploadUrlCommand) -> str:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        return await self._s3_provider.generate_part_upload_url(
            bucket=settings.s3_private_bucket_name,
            key=video.s3_key,
            upload_id=video.upload_id,
            part_number=command.part_number,
            expires_in=120,
        )
