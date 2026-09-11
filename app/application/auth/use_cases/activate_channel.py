from dataclasses import dataclass

from app.application.auth.commands import ActivateChannelCommand
from app.application.common.interfaces.auth_code import IAuthCodeService
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.auth.exceptions import ChannelAlreadyActivatedError
from app.domain.channels.service import IChannelService


@dataclass
class ActivateChannelUseCase:
    _channel_service: IChannelService
    _auth_code_service: IAuthCodeService
    _transaction_manager: ITransactionManager

    async def execute(self, command: ActivateChannelCommand) -> None:
        channel = await self._channel_service.try_get_by_id(id=command.current_channel_id)
        if channel.is_active:
            raise ChannelAlreadyActivatedError

        await self._auth_code_service.validate_activation_code(channel_id=channel.id, code=command.code)

        async with self._transaction_manager:
            await self._channel_service.try_activate(id=channel.id)
