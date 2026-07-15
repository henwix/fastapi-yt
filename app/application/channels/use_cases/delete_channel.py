from dataclasses import dataclass

from app.application.channels.commands import DeleteChannelCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService


@dataclass
class DeleteChannelUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteChannelCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        async with self._transaction_manager:
            await self._channel_service.try_delete_by_id(id=channel.id)
