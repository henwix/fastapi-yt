from dataclasses import dataclass
from uuid import UUID

from app.application.auth.commands import LoginWithEmailCodeConfirmCommand
from app.application.common.dto.jwt import JWTTokens
from app.application.common.interfaces.security import IAuthCodeService, IAuthService
from app.domain.auth.exceptions import ChannelInvalidEmailUIDError
from app.domain.channels.services import IChannelService
from app.utils.base64url import base64url_decode


@dataclass
class LoginWithEmailCodeConfirmUseCase:
    _auth_code_service: IAuthCodeService
    _auth_service: IAuthService
    _channel_service: IChannelService

    async def execute(self, command: LoginWithEmailCodeConfirmCommand) -> JWTTokens:
        try:
            decoded_channel_id = base64url_decode(value=command.uid)
            channel_id = UUID(decoded_channel_id)
        except Exception as e:
            raise ChannelInvalidEmailUIDError(uid=command.uid, exc_details=str(e)) from e

        await self._auth_code_service.validate_login_email_code(channel_id=channel_id, code=command.code)

        channel = await self._channel_service.try_get_by_id(id=channel_id)
        return await self._auth_service.login(channel_id=channel.id)
