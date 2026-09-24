from dataclasses import dataclass

from app.application.auth.commands import LoginWithEmailCodeCommand
from app.application.common.interfaces.email import IEmailService
from app.application.common.interfaces.security import IAuthCodeService
from app.domain.channels.services import IChannelService
from app.utils.base64url import base64url_encode


@dataclass
class LoginWithEmailCodeUseCase:
    _channel_service: IChannelService
    _auth_code_service: IAuthCodeService
    _email_service: IEmailService

    async def execute(self, command: LoginWithEmailCodeCommand) -> None:
        channel = await self._channel_service.get_by_email(email=command.email)
        if channel is None:
            return

        code = await self._auth_code_service.create_login_email_code(channel_id=channel.id)
        uid = base64url_encode(value=str(channel.id))
        confirmation_url = self._auth_code_service.build_login_email_confirm_url(code=code, uid=uid)
        await self._email_service.schedule_send_login_email_code(
            email=channel.email.to_raw(),
            name=channel.name.to_raw(),
            confirmation_url=confirmation_url,
            code=code,
            uid=uid,
        )
