from dataclasses import dataclass

from app.application.channels.commands import SetChannelPasswordCommand
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService


@dataclass
class SetChannelPasswordUseCase:
    channel_service: IChannelService
    transaction_manager: ITransactionManager
    password_hasher: IPasswordHasher

    async def execute(self, command: SetChannelPasswordCommand) -> None:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            new_password_hash = self.password_hasher.get_password_hash(password=command.new_password)
            channel.set_password(password_hash=new_password_hash)
            await self.channel_service.try_set_password(
                id=channel.id,
                password_hash=channel.password_hash,
            )
