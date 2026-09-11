import asyncio
from dataclasses import dataclass

from app.application.auth.commands import LoginChannelCommand
from app.application.common.dto.jwt import JWTTokens
from app.application.common.interfaces.auth import IAuthService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.auth.exceptions import IncorrectEmailOrPasswordError
from app.domain.channels.service import IChannelService

password_hash_semaphore = asyncio.Semaphore(2)


@dataclass
class LoginChannelUseCase:
    _channel_service: IChannelService
    _password_hasher: IPasswordHasher
    _auth_service: IAuthService

    async def execute(self, command: LoginChannelCommand) -> JWTTokens:
        channel = await self._channel_service.get_by_email(email=command.email)
        if not channel:
            async with password_hash_semaphore:
                await asyncio.to_thread(self._password_hasher.verify_password_hash, password=command.password)
            raise IncorrectEmailOrPasswordError

        async with password_hash_semaphore:
            if not await asyncio.to_thread(
                self._password_hasher.verify_password_hash, command.password, channel.password_hash
            ):
                raise IncorrectEmailOrPasswordError

        return await self._auth_service.login(channel_id=channel.id)
