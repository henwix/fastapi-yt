from dataclasses import dataclass

from app.application.commands.channels import UpdateChannelCommand
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty


@dataclass
class UpdateChannelUseCase:
    channel_service: IChannelService
    transaction_manager: ITransactionManager

    async def execute(self, command: UpdateChannelCommand) -> Channel:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)
            if command.slug is not Empty.UNSET:
                await self.channel_service.check_slug_exists(slug=command.slug)
            channel.update(
                name=command.name,
                slug=command.slug,
                description=command.description,
                country=command.country,
            )
            return await self.channel_service.try_update(channel=channel)
