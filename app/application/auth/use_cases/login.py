from dataclasses import dataclass

from app.application.auth.commands import LoginCommand
from app.application.common.interfaces.jwt import IJWTService
from app.application.common.interfaces.password_hasher import IPasswordHasher
from app.domain.auth.exceptions import IncorrectEmailOrPasswordError
from app.domain.channels.services import IChannelService


@dataclass
class LoginUseCase:
    _channel_service: IChannelService
    _password_hasher: IPasswordHasher
    _jwt_service: IJWTService

    async def execute(self, command: LoginCommand) -> dict[str, str]:
        channel = await self._channel_service.get_by_email(email=command.email)
        if not channel or not channel.is_active:
            self._password_hasher.verify_password_hash(password=command.password)
            raise IncorrectEmailOrPasswordError

        if not self._password_hasher.verify_password_hash(password=command.password, hash=channel.password_hash):
            raise IncorrectEmailOrPasswordError

        return self._jwt_service.create_tokens(sub=channel.id)
