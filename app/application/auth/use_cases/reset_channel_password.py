from dataclasses import dataclass

from app.application.auth.commands import ResetChannelPasswordCommand
from app.application.common.commands.email import SendChannelResetPasswordCodeCommand
from app.application.common.interfaces.task_queue import ITaskQueue
from app.domain.auth.services import IAuthService
from app.domain.channels.services import IChannelService
from app.utils.base64url import base64url_encode


@dataclass
class ResetChannelPasswordUseCase:
    _channel_service: IChannelService
    _auth_service: IAuthService
    _task_queue: ITaskQueue

    async def execute(self, command: ResetChannelPasswordCommand) -> None:
        channel = await self._channel_service.get_by_email(email=command.email)
        if channel is None:
            return

        code = await self._auth_service.create_reset_password_code(channel_id=channel.id)
        uid = base64url_encode(value=str(channel.id))
        confirmation_url = self._auth_service.build_reset_password_confirm_url(code=code, uid=uid)
        send_channel_reset_password_code_command = SendChannelResetPasswordCodeCommand(
            email=channel.email,
            name=channel.name,
            confirmation_url=confirmation_url,
            code=code,
            uid=uid,
        )
        await self._task_queue.send_channel_reset_password_code(command=send_channel_reset_password_code_command)
