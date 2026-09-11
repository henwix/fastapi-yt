from dataclasses import dataclass

from app.application.auth.commands import RefreshJWTTokenCommand
from app.application.common.dto.jwt import JWTTokens
from app.application.common.interfaces.auth import IAuthService


@dataclass
class RefreshJWTTokenUseCase:
    _auth_service: IAuthService

    async def execute(self, command: RefreshJWTTokenCommand) -> JWTTokens:
        return await self._auth_service.refresh(refresh=command.refresh)
