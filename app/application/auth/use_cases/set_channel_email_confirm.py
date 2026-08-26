from dataclasses import dataclass

from app.application.auth.commands import SetChannelEmailConfirmCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.auth.service import IAuthService
from app.domain.channels.service import IChannelService


@dataclass
class SetChannelEmailConfirmUseCase:
    _channel_service: IChannelService
    _auth_service: IAuthService
    _transaction_manager: ITransactionManager

    async def execute(self, command: SetChannelEmailConfirmCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        new_email = await self._auth_service.validate_set_email_code(channel_id=channel.id, code=command.code)

        channel.set_email(email=new_email)
        async with self._transaction_manager:
            await self._channel_service.try_update(channel=channel)
