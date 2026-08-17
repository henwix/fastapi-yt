from dataclasses import dataclass
from uuid import UUID

from app.application.auth.commands import ActivateChannelCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.auth.exceptions import ChannelActivationInvalidIdError
from app.domain.auth.services import IAuthService
from app.domain.channels.services import IChannelService
from app.utils.base64url import base64url_decode


@dataclass
class ActivateChannelUseCase:
    _channel_service: IChannelService
    _auth_service: IAuthService
    _transaction_manager: ITransactionManager

    async def execute(self, command: ActivateChannelCommand) -> None:
        try:
            decoded_channel_id = base64url_decode(value=command.uid)
            channel_id = UUID(decoded_channel_id)
        except Exception as e:
            raise ChannelActivationInvalidIdError(uid=command.uid, exc_details=str(e)) from e

        await self._auth_service.validate_activation_code(channel_id=channel_id, code=command.code)

        async with self._transaction_manager:
            await self._channel_service.try_activate(id=channel_id)
