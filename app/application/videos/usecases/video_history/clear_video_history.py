from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import ClearVideoHistoryCommand
from app.domain.channels.services import IChannelService
from app.domain.videos.services import IVideoHistoryService


@dataclass
class ClearVideoHistoryUseCase:
    _channel_service: IChannelService
    _video_history_service: IVideoHistoryService
    _tm: ITransactionManager

    async def execute(self, command: ClearVideoHistoryCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            await self._video_history_service.try_clear(channel_id=channel.id)
