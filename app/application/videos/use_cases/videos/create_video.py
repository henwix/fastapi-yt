from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CreateVideoCommand
from app.domain.channels.service import IChannelService
from app.domain.videos.entities import Video
from app.domain.videos.service import IVideoService


@dataclass
class CreateVideoUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoCommand) -> Video:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video_entity = Video.create(
            channel_id=channel.id,
            title=command.title,
            description=command.description,
            privacy_status=command.privacy_status,
        )
        async with self._transaction_manager:
            return await self._video_service.create(video=video_entity)
