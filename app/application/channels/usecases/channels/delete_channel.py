from dataclasses import dataclass

from app.application.channels.commands import DeleteChannelCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService
from app.domain.common.value_objects import DeletionTime


@dataclass
class DeleteChannelUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteChannelCommand) -> None:
        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        channel.deleted_at = DeletionTime.create_deleted()
        async with self._transaction_manager:
            await self._channel_service.try_update(channel=channel)
