from dataclasses import dataclass

from app.application.common.commands.email import (
    SendChannelActivationCodeCommand,
    SendChannelResetPasswordCodeCommand,
    SendChannelSetEmailCodeCommand,
)
from app.application.common.interfaces.task_queues.email import IEmailTaskQueue
from app.infrastructure.taskiq.tasks.email import (
    send_channel_activation_code_task,
    send_channel_reset_password_code_task,
    send_channel_set_email_code_task,
)


@dataclass
class TaskiqEmailTaskQueue(IEmailTaskQueue):
    async def send_channel_activation_code(self, command: SendChannelActivationCodeCommand) -> None:
        await send_channel_activation_code_task.kiq(command=command)

    async def send_channel_set_email_code(self, command: SendChannelSetEmailCodeCommand) -> None:
        await send_channel_set_email_code_task.kiq(command=command)

    async def send_channel_reset_password_code(self, command: SendChannelResetPasswordCodeCommand) -> None:
        await send_channel_reset_password_code_task.kiq(command=command)
