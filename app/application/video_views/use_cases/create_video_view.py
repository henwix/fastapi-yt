from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_views.commands import CreateVideoViewCommand
from app.domain.channels.services import IChannelService
from app.domain.video_views.entities import VideoView
from app.domain.video_views.services import IVideoViewService
from app.domain.videos.services import IVideoService


@dataclass
class CreateVideoViewUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_view_service: IVideoViewService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoViewCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_completed_by_id(id=command.video_id)
        video_view_entity = VideoView.create(video_id=video.id, channel_id=channel.id)
        async with self._transaction_manager:
            await self._video_view_service.create(video_view=video_view_entity)
