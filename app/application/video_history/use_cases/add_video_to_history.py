from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_history.commands import AddVideoToHistoryCommand
from app.domain.channels.service import IChannelService
from app.domain.video_history.entities import VideoHistoryItem
from app.domain.video_history.service import IVideoHistoryService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError
from app.domain.videos.service import IVideoService


@dataclass
class AddVideoToHistoryUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_history_service: IVideoHistoryService
    _transaction_manager: ITransactionManager

    async def execute(self, command: AddVideoToHistoryCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_completed_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE and video.channel_id != channel.id:
            raise VideoAccessForbiddenError(video_id=video.id, channel_id=channel.id)

        video_history_item_entity = VideoHistoryItem.create(channel_id=channel.id, video_id=video.id)

        async with self._transaction_manager:
            await self._video_history_service.upsert(video_history_item=video_history_item_entity)
