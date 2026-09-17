from dataclasses import dataclass

from app.application.auth.commands import LogoutCommand
from app.application.common.interfaces.security.auth_service import IAuthService


@dataclass
class LogoutUseCase:
    _auth_service: IAuthService

    async def execute(self, command: LogoutCommand) -> None:
        await self._auth_service.logout(refresh=command.refresh)
