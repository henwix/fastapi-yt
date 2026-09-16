from dataclasses import dataclass

from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import DeleteVideoThumbnailCommand
from app.core.configs import settings
from app.domain.channels.service import IChannelService
from app.domain.videos.exceptions import VideoThumbnailNotFoundError
from app.domain.videos.service import IVideoService


@dataclass
class DeleteVideoThumbnailUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_service: IS3Service
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoThumbnailCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)
        if video.thumbnail_s3_key is None:
            raise VideoThumbnailNotFoundError(video_id=video.id)

        video_thumbnail_s3_key = video.thumbnail_s3_key

        video.set_thumbnail_s3_key(value=None)
        async with self._transaction_manager:
            await self._video_service.try_update(video=video)

        await self._s3_service.schedule_delete_object(
            bucket=settings.s3_public_bucket_name,
            key=video_thumbnail_s3_key,
        )
