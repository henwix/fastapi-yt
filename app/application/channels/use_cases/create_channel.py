import asyncio
from dataclasses import dataclass

from app.application.channels.commands import CreateChannelCommand
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.auth.services import IAuthService
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService
from app.utils.base64url import base64url_encode

password_hash_semaphore = asyncio.Semaphore(2)


@dataclass
class CreateChannelUseCase:
    _password_hasher: IPasswordHasher
    _channel_service: IChannelService
    _auth_service: IAuthService
    _task_queue: ITaskQueue
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateChannelCommand) -> tuple[Channel, bool]:
        await self._channel_service.check_email_exists(email=command.email)
        await self._channel_service.check_slug_exists(slug=command.slug)

        async with password_hash_semaphore:
            password_hash = await asyncio.to_thread(self._password_hasher.get_password_hash, command.password)

        activation_required = settings.email_send_activation_email

        channel_entity = Channel.create(
            email=command.email,
            name=command.name,
            slug=command.slug,
            password_hash=password_hash,
            description=command.description,
            country=command.country,
            is_active=not activation_required,
        )

        async with self._transaction_manager:
            channel = await self._channel_service.create(channel=channel_entity)

        if activation_required:
            code = await self._auth_service.create_activation_code(channel_id=channel.id)
            await self._task_queue.send_activation_email(
                recipients=[channel.email],
                template_context={
                    'name': channel.name,
                    'email': channel.email,
                    'code': code,
                    'channel_id': base64url_encode(value=str(channel.id)),
                },
            )
        return channel, activation_required
