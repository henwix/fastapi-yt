from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.commands.s3 import AbortMultipartUploadCommand, DeleteS3ObjectCommand
from app.application.common.use_cases.s3.abort_multipart_upload import AbortMultipartUploadUseCase
from app.application.common.use_cases.s3.delete_s3_object import DeleteS3ObjectUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='s3_delete_object_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def s3_delete_object_task(
    command: DeleteS3ObjectCommand,
    use_case: FromDishka[DeleteS3ObjectUseCase],
) -> None:
    await use_case.execute(command=command)


@broker.task(task_name='s3_abort_multipart_upload_task', retry_on_error=True, max_retries=3, delay=15)
@inject(patch_module=True)
async def s3_abort_multipart_upload_task(
    command: AbortMultipartUploadCommand,
    use_case: FromDishka[AbortMultipartUploadUseCase],
):
    await use_case.execute(command=command)
