from dataclasses import dataclass

from app.application.commands.channels import CreateChannelCommand
from app.application.common.password_hasher import IPasswordHasher
from app.application.common.transaction_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.repository import IChannelRepository
from app.domain.channels.services import IChannelValidatorService


@dataclass
class CreateChannelUseCase:
    password_hasher: IPasswordHasher
    channel_validator_service: IChannelValidatorService
    channel_repository: IChannelRepository
    transaction_manager: ITransactionManager

    async def execute(self, command: CreateChannelCommand) -> Channel:
        async with self.transaction_manager:
            await self.channel_validator_service.validate(email=command.email, slug=command.slug)

            channel_entity = Channel.create(
                email=command.email,
                name=command.name,
                slug=command.slug,
                password_hash=self.password_hasher.get_password_hash(password=command.password),
                description=command.description,
                country=command.country,
            )
            created_channel = await self.channel_repository.create(channel=channel_entity)
        return created_channel
