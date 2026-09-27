from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import DeleteVideoFromHistoryCommand
from app.domain.channels.services import IChannelService
from app.domain.videos.services import IVideoHistoryService


@dataclass
class DeleteVideoFromHistoryUseCase:
    _channel_service: IChannelService
    _video_history_service: IVideoHistoryService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoFromHistoryCommand) -> None:
        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        async with self._transaction_manager:
            await self._video_history_service.try_delete(channel_id=channel.id, video_id=command.video_id)
