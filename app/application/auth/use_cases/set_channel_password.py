import asyncio
from dataclasses import dataclass

from app.application.auth.commands import SetChannelPasswordCommand
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.service import IChannelService

password_hash_semaphore = asyncio.Semaphore(2)


@dataclass
class SetChannelPasswordUseCase:
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager
    _password_hasher: IPasswordHasher

    async def execute(self, command: SetChannelPasswordCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        async with password_hash_semaphore:
            new_password_hash = await asyncio.to_thread(self._password_hasher.get_password_hash, command.new_password)

        async with self._transaction_manager:
            await self._channel_service.try_set_password(
                id=channel.id,
                password_hash=new_password_hash,
            )
