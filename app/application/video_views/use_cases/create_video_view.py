from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_views.commands import CreateVideoViewCommand
from app.domain.channels.services import IChannelService
from app.domain.video_views.entities import VideoView
from app.domain.video_views.services import IVideoViewService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError
from app.domain.videos.services import IVideoService


@dataclass
class CreateVideoViewUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_view_service: IVideoViewService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoViewCommand) -> None:
        channel = None
        if command.current_channel_id is not None:
            channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        video = await self._video_service.try_get_completed_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            if channel is None:
                raise VideoAccessForbiddenError(video_id=video.id)
            self._video_service.ensure_video_access(video=video, channel=channel)

        video_view_entity = VideoView.create(
            video_id=video.id,
            channel_id=channel.id if channel is not None else None,
            anonymous_id=command.anonymous_id if channel is None else None,
        )

        async with self._transaction_manager:
            await self._video_view_service.try_upsert(video_view=video_view_entity)
            await self._video_service.try_increase_views_count(video_id=video.id)
