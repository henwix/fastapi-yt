from dataclasses import dataclass

from app.application.commands.channels import CreateChannelCommand
from app.application.common.password_hasher import IPasswordHasher
from app.application.common.transcation_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.exceptions import ChannelWithEmailAlreadyExists, ChannelWithSlugAlreadyExists
from app.domain.channels.repository import IChannelRepository


@dataclass
class CreateChannelUseCase:
    password_hasher: IPasswordHasher
    channels_repository: IChannelRepository
    transaction_manager: ITransactionManager

    async def execute(self, command: CreateChannelCommand) -> Channel:
        async with self.transaction_manager:
            if await self.channels_repository.check_channel_exists_by_email(email=command.email):
                raise ChannelWithEmailAlreadyExists(email=command.email)
            if await self.channels_repository.check_channel_exists_by_slug(slug=command.slug):
                raise ChannelWithSlugAlreadyExists(slug=command.slug)

            channel_entity = Channel.create(
                email=command.email,
                name=command.name,
                slug=command.slug,
                password_hash=self.password_hasher.get_password_hash(password=command.password),
                description=command.description,
                country=command.country,
            )
            created_channel = await self.channels_repository.create(channel=channel_entity)
        return created_channel
