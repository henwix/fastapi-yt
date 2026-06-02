from dataclasses import dataclass

from app.application.commands.channels import DeleteChannelCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.repository import IChannelRepository


@dataclass
class DeleteChannelUseCase:
    channel_repository: IChannelRepository
    transaction_manager: ITransactionManager

    async def execute(self, command: DeleteChannelCommand) -> bool:
        async with self.transaction_manager:
            channel = await self.channel_repository.try_get_active_by_id(id=command.channel_id)
            return await self.channel_repository.try_delete_by_id(id=channel.id)
