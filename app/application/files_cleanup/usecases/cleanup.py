from dataclasses import dataclass

from app.application.common.interfaces.s3 import IS3Service
from app.domain.files_cleanup.services import IFileCleanupService


@dataclass
class CleanupUseCase:
    _file_cleanup_service: IFileCleanupService
    _s3_service: IS3Service

    async def execute(self) -> int:
        total_deleted_files = 0

        while True:
            cleanups = await self._file_cleanup_service.get_for_cleanup(limit=500)
            if not cleanups:
                break

            buckets: dict[str, list[str]] = {}
            for cleanup in cleanups:
                bucket_keys = buckets.get(cleanup.bucket)
                if bucket_keys is not None:
                    bucket_keys.append(cleanup.s3_key)
                else:
                    buckets[cleanup.bucket] = [cleanup.s3_key]

            # for bucket, keys in buckets.items():
            #     ...

        return total_deleted_files
