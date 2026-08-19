from dataclasses import dataclass

from app.application.common.commands.email import (
    SendChannelActivationCodeCommand,
    SendChannelResetPasswordCodeCommand,
    SendChannelSetEmailCodeCommand,
)
from app.application.common.interfaces.task_queue import ITaskQueue
from app.infrastructure.taskiq.tasks.email import (
    send_channel_activation_code_task,
    send_channel_reset_password_code_task,
    send_channel_set_email_code_task,
)
from app.infrastructure.taskiq.tasks.s3 import s3_abort_multipart_upload_task, s3_delete_object_task


@dataclass
class TaskiqTaskQueue(ITaskQueue):
    async def delete_s3_object(
        self,
        bucket: str,
        key: str,
    ) -> None:
        await s3_delete_object_task.kiq(bucket=bucket, key=key)

    async def abort_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
    ) -> None:
        await s3_abort_multipart_upload_task.kiq(bucket=bucket, key=key, upload_id=upload_id)

    async def send_channel_activation_code(self, command: SendChannelActivationCodeCommand) -> None:
        await send_channel_activation_code_task.kiq(command=command)

    async def send_channel_set_email_code(self, command: SendChannelSetEmailCodeCommand) -> None:
        await send_channel_set_email_code_task.kiq(command=command)

    async def send_channel_reset_password_code(self, command: SendChannelResetPasswordCodeCommand) -> None:
        await send_channel_reset_password_code_task.kiq(command=command)
