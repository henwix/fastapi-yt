from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.s3 import DeleteS3ObjectCommand
from app.application.common.interfaces.s3.provider import IS3Provider
from app.domain.common.exceptions import AppException

logger = getLogger(__name__)


@dataclass
class DeleteS3ObjectUseCase:
    _s3_provider: IS3Provider

    async def execute(self, command: DeleteS3ObjectCommand) -> None:
        logger.info('Start S3 file deletion', extra={'log_meta': {'bucket': command.bucket, 'key': command.key}})
        try:
            await self._s3_provider.delete_object(bucket=command.bucket, key=command.key)
        except AppException as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info('Complete S3 file deletion', extra={'log_meta': {'bucket': command.bucket, 'key': command.key}})
