from dataclasses import dataclass

from app.application.commands.channels import DeleteChannelCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.services import IChannelService


@dataclass
class DeleteChannelUseCase:
    channel_service: IChannelService
    transaction_manager: ITransactionManager

    async def execute(self, command: DeleteChannelCommand) -> None:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            await self.channel_service.try_delete_by_id(id=channel.id)
