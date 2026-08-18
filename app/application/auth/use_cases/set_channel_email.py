from dataclasses import dataclass

from app.application.auth.commands import SetChannelEmailCommand
from app.application.common.interfaces.task_queue import ITaskQueue
from app.domain.auth.exceptions import ChannelEmailAlreadyAssociatedWithThisAcccountError
from app.domain.auth.services import IAuthService
from app.domain.channels.services import IChannelService


@dataclass
class SetChannelEmailUseCase:
    _channel_service: IChannelService
    _auth_service: IAuthService
    _task_queue: ITaskQueue

    async def execute(self, command: SetChannelEmailCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        if channel.email == command.new_email:
            raise ChannelEmailAlreadyAssociatedWithThisAcccountError(channel_id=channel.id)

        await self._channel_service.try_check_email_exists(email=command.new_email)

        code = await self._auth_service.create_set_email_code(channel_id=channel.id, new_email=command.new_email)
        confirmation_url = self._auth_service.build_set_email_confirm_url(code=code)
        await self._task_queue.send_channel_set_email_code(
            recipients=[command.new_email],
            template_context={
                'name': channel.name,
                'email': command.new_email,
                'confirmation_url': confirmation_url,
                'code': code,
            },
        )
