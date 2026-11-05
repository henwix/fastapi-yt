from dataclasses import asdict, dataclass
from logging import getLogger

from app.application.common.commands.s3 import AbortMultipartUploadCommand
from app.application.common.interfaces.s3 import IS3Provider
from app.domain.common.exceptions.base import AppError
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService

logger = getLogger(__name__)


@dataclass
class AbortMultipartUploadUseCase:
    _s3_provider: IS3Provider
    _file_cleanup_service: IFileCleanupService

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
            logger.info(
                'Multipart upload aborted',
                extra={
                    'log_meta': {'bucket': command.bucket, 'key': command.key, 'upload_id': command.upload_id},
                },
            )
            file_cleanup = FileCleanup.create(key=command.key, bucket=command.bucket)
            await self._file_cleanup_service.upsert(cleanup=file_cleanup)
            logger.info(
                'FileCleanup successfully created',
                extra={
                    'log_meta': {'bucket': command.bucket, 'key': command.key},
                },
            )
        except AppError as e:
            logger.exception(msg=e.message, extra={'log_meta': asdict(e)})
            raise
        logger.info(
            'Complete S3 abort multipart upload',
            extra={
                'log_meta': {'bucket': command.bucket, 'key': command.key, 'upload_id': command.upload_id},
            },
        )
