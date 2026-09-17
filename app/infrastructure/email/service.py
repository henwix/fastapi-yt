from dataclasses import dataclass

from app.application.common.commands.email import (
    SendChannelActivationCodeCommand,
    SendChannelResetPasswordCodeCommand,
    SendChannelSetEmailCodeCommand,
)
from app.application.common.interfaces.email import IEmailService
from app.infrastructure.taskiq.tasks import (
    send_channel_activation_code_task,
    send_channel_reset_password_code_task,
    send_channel_set_email_code_task,
)


@dataclass
class EmailService(IEmailService):
    async def schedule_send_channel_activation_code(
        self, email: str, name: str, activation_url: str, code: str
    ) -> None:
        command = SendChannelActivationCodeCommand(email=email, name=name, activation_url=activation_url, code=code)
        await send_channel_activation_code_task.kiq(command=command)

    async def schedule_send_channel_set_email_code(
        self, email: str, name: str, confirmation_url: str, code: str
    ) -> None:
        command = SendChannelSetEmailCodeCommand(email=email, name=name, confirmation_url=confirmation_url, code=code)
        await send_channel_set_email_code_task.kiq(command=command)

    async def schedule_send_channel_reset_password_code(
        self, email: str, name: str, confirmation_url: str, code: str, uid: str
    ) -> None:
        command = SendChannelResetPasswordCodeCommand(
            email=email,
            name=name,
            confirmation_url=confirmation_url,
            code=code,
            uid=uid,
        )
        await send_channel_reset_password_code_task.kiq(command=command)
