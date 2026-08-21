from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.s3 import AbortMultipartUploadCommand
from app.application.common.interfaces.s3_provider import IS3Provider
from app.domain.common.exceptions import AppException

logger = getLogger(__name__)


@dataclass
class AbortMultipartUploadUseCase:
    _s3_provider: IS3Provider

    async def execute(self, command: AbortMultipartUploadCommand) -> None:
        logger.info(
            'Start S3 abort multipart upload',
            extra={
                'log_meta': {'bucket': command.bucket, 'key': command.key, 'upload_id': command.upload_id},
            },
        )
        try:
            await self._s3_provider.abort_multipart_upload(
                bucket=command.bucket, key=command.key, upload_id=command.upload_id
            )
        except AppException as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info(
            'Complete S3 abort multipart upload',
            extra={
                'log_meta': {'bucket': command.bucket, 'key': command.key, 'upload_id': command.upload_id},
            },
        )
