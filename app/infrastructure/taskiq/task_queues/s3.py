from app.application.common.commands.s3 import AbortMultipartUploadCommand, DeleteS3ObjectCommand
from app.application.common.interfaces.task_queues.s3 import IS3TaskQueue
from app.infrastructure.taskiq.tasks.s3 import s3_abort_multipart_upload_task, s3_delete_object_task


class TaskiqS3TaskQueue(IS3TaskQueue):
    async def delete_s3_object(self, command: DeleteS3ObjectCommand) -> None:
        await s3_delete_object_task.kiq(command)

    async def abort_multipart_upload(self, command: AbortMultipartUploadCommand) -> None:
        await s3_abort_multipart_upload_task.kiq(command=command)
