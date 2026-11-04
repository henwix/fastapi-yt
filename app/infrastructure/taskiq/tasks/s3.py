from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.commands.s3 import AbortMultipartUploadCommand
from app.application.common.usecases.s3 import AbortMultipartUploadUseCase
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()


@broker.task(task_name='s3_abort_multipart_upload_task', retry_on_error=True, max_retries=3, delay=15)
@inject(patch_module=True)
async def s3_abort_multipart_upload_task(
    command: AbortMultipartUploadCommand,
    use_case: FromDishka[AbortMultipartUploadUseCase],
):
    await use_case.execute(command=command)
