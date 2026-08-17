from dataclasses import dataclass

from app.application.auth.commands import ResendChannelActivationCodeCommand
from app.application.common.interfaces.task_queue import ITaskQueue
from app.core.configs import settings
from app.domain.auth.exceptions import ChannelActivationDisabledError
from app.domain.auth.services import IAuthService
from app.domain.channels.services import IChannelService
from app.utils.base64url import base64url_encode


@dataclass
class ResendChannelActivationCodeUseCase:
    _channel_service: IChannelService
    _auth_service: IAuthService
    _task_queue: ITaskQueue

    async def execute(self, command: ResendChannelActivationCodeCommand) -> None:
        if not settings.auth_send_activation_email:
            raise ChannelActivationDisabledError

        channel = await self._channel_service.get_by_email(email=command.email)
        if channel is None or channel.is_active:
            return None

        code = await self._auth_service.create_activation_code(channel_id=channel.id)
        uid = base64url_encode(value=str(channel.id))
        activation_url = self._auth_service.build_activation_url(code=code, uid=uid)
        await self._task_queue.send_channel_activation_code(
            recipients=[channel.email],
            template_context={
                'name': channel.name,
                'email': channel.email,
                'activation_url': activation_url,
                'code': code,
                'uid': uid,
            },
        )
