import asyncio
from dataclasses import dataclass
from uuid import UUID

from app.application.auth.commands import ResetChannelPasswordConfirmCommand
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.auth.exceptions import ChannelInvalidEmailUIDError
from app.domain.auth.service import IAuthService
from app.domain.channels.service import IChannelService
from app.utils.base64url import base64url_decode

password_hash_semaphore = asyncio.Semaphore(2)


@dataclass
class ResetChannelPasswordConfirmUseCase:
    _auth_service: IAuthService
    _channel_service: IChannelService
    _password_hasher: IPasswordHasher
    _transaction_manager: ITransactionManager

    async def execute(self, command: ResetChannelPasswordConfirmCommand) -> None:
        try:
            decoded_channel_id = base64url_decode(value=command.uid)
            channel_id = UUID(decoded_channel_id)
        except Exception as e:
            raise ChannelInvalidEmailUIDError(uid=command.uid, exc_details=str(e)) from e

        await self._auth_service.validate_reset_password_code(channel_id=channel_id, code=command.code)

        async with password_hash_semaphore:
            new_password_hash = await asyncio.to_thread(self._password_hasher.get_password_hash, command.new_password)

        async with self._transaction_manager:
            await self._channel_service.try_set_password(id=channel_id, password_hash=new_password_hash)
