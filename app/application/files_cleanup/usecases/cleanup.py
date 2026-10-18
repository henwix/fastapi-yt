from dataclasses import dataclass
from logging import getLogger
from uuid import UUID

from app.application.common.interfaces.s3 import IS3Service
from app.application.files_cleanup.dto import CleanupResultDTO
from app.domain.common.exceptions.s3 import S3ResponseError
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.domain.files_cleanup.services import IFileCleanupService

logger = getLogger(__name__)


@dataclass
class CleanupUseCase:
    _file_cleanup_service: IFileCleanupService
    _s3_service: IS3Service

    async def execute(self) -> CleanupResultDTO:
        total_files_deleted = 0
        total_files_failed = 0

        logger.info('Starting cleanup')
        while True:
            cleanups = await self._file_cleanup_service.get_for_cleanup(limit=500)
            logger.info(f'Retrieved {len(cleanups)} files')
            if not cleanups:
                logger.info('No files found, stop cycle')
                break

            buckets: dict[str, list[FileCleanup]] = {}
            for cleanup in cleanups:
                bucket_cleanups = buckets.get(cleanup.bucket)
                if bucket_cleanups is not None:
                    bucket_cleanups.append(cleanup)
                else:
                    buckets[cleanup.bucket] = [cleanup]

            logger.info(f'Found {len(buckets)} buckets for cleanup')
            for bucket_name, bucket_cleanups in buckets.items():
                keys = [cleanup.s3_key for cleanup in bucket_cleanups]
                try:
                    response = await self._s3_service.delete_objects(bucket=bucket_name, keys=keys)
                except S3ResponseError as e:
                    match e.error_code:
                        case 'NoSuchBucket' | 'InvalidBucketName' | 'AccessDenied':
                            failed = await self._file_cleanup_service.update_many(
                                cleanups=bucket_cleanups,
                                status=FileCleanupStatusEnum.FAILED,
                                error_code=e.error_code,
                                error_message=e.error_message,
                            )
                            logger.info(
                                f'{failed} files failed to delete from bucket {bucket_name}',
                                extra={
                                    'log_meta': {
                                        'error_code': e.error_code,
                                        'error_message': e.error_message,
                                        'error_status': e.error_status,
                                    }
                                },
                            )
                            total_files_failed += failed
                            continue
                        case _:
                            raise

                response_errors = response.get('Errors', [])
                if not response_errors:
                    ids = [cleanup.id for cleanup in bucket_cleanups]
                    deleted = await self._file_cleanup_service.delete_many(ids=ids)
                    logger.info(f'{deleted} files deleted from bucket {bucket_name}')
                    total_files_deleted += deleted
                else:
                    errors_by_key: dict[str, dict[str, str]] = {error['Key']: error for error in response_errors}
                    to_delete: list[UUID] = []
                    to_update: list[dict[str, str | UUID]] = []

                    for cleanup in bucket_cleanups:
                        error = errors_by_key.get(cleanup.s3_key)
                        if error is None:
                            to_delete.append(cleanup.id)
                        else:
                            to_update.append(
                                {
                                    'id': cleanup.id,
                                    'status': FileCleanupStatusEnum.FAILED.value,
                                    'error_code': error['Code'],
                                    'error_message': error['Message'],
                                }
                            )
                    deleted = await self._file_cleanup_service.delete_many(ids=to_delete)
                    failed = await self._file_cleanup_service.update_bulk(data=to_update)
                    logger.info(f'{deleted} files deleted from bucket {bucket_name}')
                    logger.info(f'{failed} files failed to delete from bucket {bucket_name}')
                    total_files_deleted += deleted
                    total_files_failed += failed

        return CleanupResultDTO(total_deleted=total_files_deleted, total_failed=total_files_failed)
