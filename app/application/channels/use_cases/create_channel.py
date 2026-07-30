import asyncio
from dataclasses import dataclass

from app.application.channels.commands import CreateChannelCommand
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService

password_hash_semaphore = asyncio.Semaphore(2)


@dataclass
class CreateChannelUseCase:
    _password_hasher: IPasswordHasher
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateChannelCommand) -> Channel:
        await self._channel_service.check_email_exists(email=command.email)
        await self._channel_service.check_slug_exists(slug=command.slug)

        async with password_hash_semaphore:
            password_hash = await asyncio.to_thread(self._password_hasher.get_password_hash, command.password)

        channel_entity = Channel.create(
            email=command.email,
            name=command.name,
            slug=command.slug,
            password_hash=password_hash,
            description=command.description,
            country=command.country,
        )

        async with self._transaction_manager:
            return await self._channel_service.create(channel=channel_entity)
