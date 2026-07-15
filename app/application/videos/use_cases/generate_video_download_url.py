from dataclasses import dataclass

from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.videos.commands import GenerateVideoDownloadUrlCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError
from app.domain.videos.services import IVideoService


@dataclass
class GenerateVideoDownloadUrlUseCase:
    _video_service: IVideoService
    _channel_service: IChannelService
    _s3_provider: IS3Provider

    async def execute(self, command: GenerateVideoDownloadUrlCommand) -> str:
        video = await self._video_service.try_get_completed_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            if command.current_channel_id is None:
                raise VideoAccessForbiddenError(video_id=video.id)
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
            self._video_service.ensure_video_access(video=video, channel=channel)

        return await self._s3_provider.generate_download_url(
            bucket=settings.s3_private_bucket_name,
            key=video.s3_key,
            expires_in=10800,
        )
