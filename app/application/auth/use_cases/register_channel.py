import asyncio
from dataclasses import dataclass

from app.application.auth.commands import RegisterChannelCommand
from app.application.common.commands.email import SendChannelActivationCodeCommand
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.application.common.interfaces.task_queues.email import IEmailTaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.core.configs import settings
from app.domain.auth.service import IAuthService
from app.domain.channels.entities import Channel
from app.domain.channels.service import IChannelService

password_hash_semaphore = asyncio.Semaphore(2)


@dataclass
class RegisterChannelUseCase:
    _password_hasher: IPasswordHasher
    _channel_service: IChannelService
    _auth_service: IAuthService
    _jwt_service: IJWTService
    _email_task_queue: IEmailTaskQueue
    _transaction_manager: ITransactionManager

    async def execute(self, command: RegisterChannelCommand) -> tuple[Channel, dict[str, str], bool]:
        await self._channel_service.try_check_email_exists(email=command.email)
        await self._channel_service.try_check_slug_exists(slug=command.slug)

        async with password_hash_semaphore:
            password_hash = await asyncio.to_thread(self._password_hasher.get_password_hash, command.password)

        activation_required = settings.auth_send_activation_email

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

        tokens = self._jwt_service.create_tokens(sub=channel.id)

        if activation_required:
            code = await self._auth_service.create_activation_code(channel_id=channel.id)
            activation_url = self._auth_service.build_activation_url(code=code)
            send_channel_activation_code_command = SendChannelActivationCodeCommand(
                email=channel.email.value,
                name=channel.name.value,
                activation_url=activation_url,
                code=code,
            )
            await self._email_task_queue.send_channel_activation_code(command=send_channel_activation_code_command)
        return channel, tokens, activation_required
