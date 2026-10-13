from dataclasses import dataclass

from app.application.auth.commands import ActivateChannelCommand
from app.application.common.interfaces.security import IAuthCodeService
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.auth.exceptions import ChannelAlreadyActivatedError
from app.domain.channels.services import IChannelService


@dataclass
class ActivateChannelUseCase:
    _channel_service: IChannelService
    _auth_code_service: IAuthCodeService
    _tm: ITransactionManager

    async def execute(self, command: ActivateChannelCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_by_id(id=command.current_channel_id)
            if channel.is_active:
                raise ChannelAlreadyActivatedError(channel_id=channel.id)

            await self._auth_code_service.validate_activation_code(channel_id=channel.id, code=command.code)

            await self._channel_service.try_activate(id=channel.id)
