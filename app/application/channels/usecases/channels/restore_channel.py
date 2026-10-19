from dataclasses import dataclass

from app.application.channels.commands import RestoreChannelCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelNotDeletedError, ChannelNotFoundByIdError
from app.domain.channels.services import IChannelService


@dataclass
class RestoreChannelUseCase:
    _channel_service: IChannelService
    _tm: ITransactionManager

    async def execute(self, command: RestoreChannelCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_by_id(id=command.current_channel_id)
            if channel.deletion_status is ChannelDeletionStatusEnum.ACTIVE:
                raise ChannelNotDeletedError(channel_id=channel.id)
            elif channel.deletion_status is ChannelDeletionStatusEnum.PURGING:
                raise ChannelNotFoundByIdError(channel_id=channel.id)
            await self._channel_service.try_restore(id=channel.id)
