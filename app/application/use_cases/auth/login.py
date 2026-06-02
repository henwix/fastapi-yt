from dataclasses import dataclass

from app.application.commands.auth import LoginCommand
from app.application.common.jwt import IJWTService
from app.application.common.password_hasher import IPasswordHasher
from app.domain.auth.exceptions import IncorrectEmailOrPasswordError
from app.domain.channels.repository import IChannelRepository


@dataclass
class LoginUseCase:
    channel_repository: IChannelRepository
    password_hasher: IPasswordHasher
    jwt_service: IJWTService

    async def execute(self, command: LoginCommand) -> dict[str, str]:
        channel = await self.channel_repository.get_by_email(email=command.email)
        if not channel or not channel.is_active:
            self.password_hasher.verify_password_hash(password=command.password)
            raise IncorrectEmailOrPasswordError

        if not self.password_hasher.verify_password_hash(password=command.password, hash=channel.password_hash):
            raise IncorrectEmailOrPasswordError

        return self.jwt_service.create_tokens(sub=channel.id)
