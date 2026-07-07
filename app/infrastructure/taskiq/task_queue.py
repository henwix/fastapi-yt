from dataclasses import dataclass

from app.application.common.interfaces.task_queue import ITaskQueue
from app.infrastructure.taskiq.tasks.delete_s3_file import delete_s3_object_task


@dataclass
class TaskiqTaskQueue(ITaskQueue):
    async def delete_s3_object(self, bucket: str, key: str) -> None:
        await delete_s3_object_task.kiq(bucket=bucket, key=key)
