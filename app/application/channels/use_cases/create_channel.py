from dataclasses import dataclass

from app.application.channels.commands import CreateChannelCommand
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService


@dataclass
class CreateChannelUseCase:
    password_hasher: IPasswordHasher
    channel_service: IChannelService
    transaction_manager: ITransactionManager

    async def execute(self, command: CreateChannelCommand) -> Channel:
        async with self.transaction_manager:
            await self.channel_service.check_email_exists(email=command.email)
            await self.channel_service.check_slug_exists(slug=command.slug)

            channel_entity = Channel.create(
                email=command.email,
                name=command.name,
                slug=command.slug,
                password_hash=self.password_hasher.get_password_hash(password=command.password),
                description=command.description,
                country=command.country,
            )
            created_channel = await self.channel_service.create(channel=channel_entity)
        return created_channel
