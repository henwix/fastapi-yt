from logging import getLogger

from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.interfaces.s3_provider import IS3Provider
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()
logger = getLogger(__name__)


@broker.task(task_name='delete_s3_object_task', retry_on_error=True, max_retries=10, delay=15)
@inject(patch_module=True)
async def delete_s3_object_task(
    s3_provider: FromDishka[IS3Provider],
    bucket: str,
    key: str,
) -> None:
    logger.info('Starting S3 file deletion', extra={'log_meta': {'bucket': bucket, 'key': key}})
    await s3_provider.delete_object(bucket=bucket, key=key)
    logger.info('Complete S3 file deletion', extra={'log_meta': {'bucket': bucket, 'key': key}})
