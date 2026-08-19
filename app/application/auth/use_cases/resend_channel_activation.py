from dataclasses import dataclass

from app.application.auth.commands import ResendChannelActivationCodeCommand
from app.application.common.commands.email import SendChannelActivationCodeCommand
from app.application.common.interfaces.task_queue import ITaskQueue
from app.domain.auth.exceptions import ChannelAlreadyActivatedError
from app.domain.auth.services import IAuthService
from app.domain.channels.services import IChannelService


@dataclass
class ResendChannelActivationCodeUseCase:
    _channel_service: IChannelService
    _auth_service: IAuthService
    _task_queue: ITaskQueue

    async def execute(self, command: ResendChannelActivationCodeCommand) -> None:
        channel = await self._channel_service.try_get_by_id(id=command.current_channel_id)
        if channel.is_active:
            raise ChannelAlreadyActivatedError

        code = await self._auth_service.create_activation_code(channel_id=channel.id)
        activation_url = self._auth_service.build_activation_url(code=code)
        send_channel_activation_code_command = SendChannelActivationCodeCommand(
            email=channel.email,
            name=channel.name,
            activation_url=activation_url,
            code=code,
        )
        await self._task_queue.send_channel_activation_code(command=send_channel_activation_code_command)
