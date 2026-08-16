from dataclasses import dataclass

from app.application.common.interfaces.task_queue import ITaskQueue
from app.infrastructure.taskiq.tasks.email import send_activation_email_task
from app.infrastructure.taskiq.tasks.s3 import s3_abort_multipart_upload_task, s3_delete_object_task


@dataclass
class TaskiqTaskQueue(ITaskQueue):
    async def delete_s3_object(self, bucket: str, key: str) -> None:
        await s3_delete_object_task.kiq(bucket=bucket, key=key)

    async def abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> None:
        await s3_abort_multipart_upload_task.kiq(bucket=bucket, key=key, upload_id=upload_id)

    async def send_activation_email(self, recipients: list[str], template_context: dict | None = None) -> None:
        await send_activation_email_task.kiq(recipients=recipients, template_context=template_context)
