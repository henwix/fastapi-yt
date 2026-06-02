from dataclasses import dataclass

from app.application.commands.channels import UpdateChannelCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.repository import IChannelRepository


@dataclass
class UpdateChannelUseCase:
    channel_repository: IChannelRepository
    transaction_manager: ITransactionManager

    async def execute(self, command: UpdateChannelCommand) -> Channel:
        async with self.transaction_manager:
            channel = await self.channel_repository.try_get_active_by_id(id=command.channel_id)
            channel.update(
                name=command.name,
                slug=command.slug,
                description=command.description,
                country=command.country,
            )
            return await self.channel_repository.update(channel=channel)
