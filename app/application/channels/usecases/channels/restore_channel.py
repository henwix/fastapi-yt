from dataclasses import dataclass

from app.application.channels.commands import RestoreChannelCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.exceptions import ChannelNotDeletedError
from app.domain.channels.services import IChannelService
from app.domain.common.value_objects import DeletionTime


@dataclass
class RestoreChannelUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager

    async def execute(self, command: RestoreChannelCommand) -> None:
        channel = await self._channel_service.try_get_by_id(id=command.current_channel_id)
        if not channel.deleted_at.is_deleted():
            raise ChannelNotDeletedError(channel_id=channel.id)

        channel.deleted_at = DeletionTime.create_not_deleted()
        async with self._transaction_manager:
            await self._channel_service.try_update(channel=channel)
