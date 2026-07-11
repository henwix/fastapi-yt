from dataclasses import asdict
from logging import getLogger

from dishka.integrations.taskiq import FromDishka, inject

from app.application.common.interfaces.s3_provider import IS3Provider
from app.domain.common.exceptions import AppException
from app.infrastructure.taskiq.broker import get_broker

broker = get_broker()
logger = getLogger(__name__)


@broker.task(task_name='s3_delete_object_task', retry_on_error=True, max_retries=10, delay=60)
@inject(patch_module=True)
async def s3_delete_object_task(
    s3_provider: FromDishka[IS3Provider],
    bucket: str,
    key: str,
) -> None:
    logger.info('Starting S3 file deletion', extra={'log_meta': {'bucket': bucket, 'key': key}})
    try:
        await s3_provider.delete_object(bucket=bucket, key=key)
    except AppException as e:
        logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
        raise
    logger.info('Complete S3 file deletion', extra={'log_meta': {'bucket': bucket, 'key': key}})


@broker.task(task_name='s3_abort_multipart_upload', retry_on_error=True, max_retries=3, delay=15)
@inject(patch_module=True)
async def s3_abort_multipart_upload(
    s3_provider: FromDishka[IS3Provider],
    bucket: str,
    key: str,
    upload_id: str,
):
    logger.info(
        'Starting S3 abort multipart upload',
        extra={
            'log_meta': {'bucket': bucket, 'key': key, 'upload_id': upload_id},
        },
    )
    try:
        await s3_provider.abort_multipart_upload(bucket=bucket, key=key, upload_id=upload_id)
    except AppException as e:
        logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
        raise
    logger.info(
        'Complete S3 abort multipart upload',
        extra={
            'log_meta': {'bucket': bucket, 'key': key, 'upload_id': upload_id},
        },
    )
