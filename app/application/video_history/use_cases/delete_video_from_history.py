from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_history.commands import DeleteVideoFromHistoryCommand
from app.domain.channels.services import IChannelService
from app.domain.video_history.services import IVideoHistoryService


@dataclass
class DeleteVideoFromHistoryUseCase:
    _channel_service: IChannelService
    _video_history_service: IVideoHistoryService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoFromHistoryCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        async with self._transaction_manager:
            await self._video_history_service.try_delete(channel_id=channel.id, video_id=command.video_id)
