from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_history.commands import ClearVideoHistoryCommand
from app.domain.channels.service import IChannelService
from app.domain.video_history.service import IVideoHistoryService


@dataclass
class ClearVideoHistoryUseCase:
    _channel_service: IChannelService
    _video_history_service: IVideoHistoryService
    _transaction_manager: ITransactionManager

    async def execute(self, command: ClearVideoHistoryCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        async with self._transaction_manager:
            await self._video_history_service.try_clear(channel_id=channel.id)
