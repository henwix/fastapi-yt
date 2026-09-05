from dataclasses import dataclass
from uuid import uuid4

from app.application.common.commands.s3 import AbortMultipartUploadCommand, DeleteS3ObjectCommand
from app.application.common.interfaces.s3.provider import IS3Provider
from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.task_queues.s3 import IS3TaskQueue


@dataclass
class S3Service(IS3Service):
    _provider: IS3Provider
    _s3_task_queue: IS3TaskQueue

    def _generate_unique_bucket_key(self, filename: str, key_prefix: str) -> str:
        return f'{key_prefix}/{uuid4().hex[:10]}_{filename}'

    async def create_multipart_upload(
        self,
        bucket: str,
        filename: str,
        content_type: str,
        key_prefix: str,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        key = self._generate_unique_bucket_key(filename=filename, key_prefix=key_prefix)
        return await self._provider.create_multipart_upload(
            bucket=bucket,
            key=key,
            content_type=content_type,
            metadata=metadata,
        )

    async def generate_upload_url(
        self,
        bucket: str,
        filename: str,
        content_type: str,
        key_prefix: str,
        expires_in: int,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        key = self._generate_unique_bucket_key(filename=filename, key_prefix=key_prefix)
        return await self._provider.generate_upload_url(
            bucket=bucket,
            key=key,
            content_type=content_type,
            expires_in=expires_in,
            metadata=metadata,
        )

    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[dict],
    ) -> dict:
        return await self._provider.complete_multipart_upload(
            bucket=bucket,
            key=key,
            upload_id=upload_id,
            parts=parts,
        )

    async def schedule_abort_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
    ) -> None:
        command = AbortMultipartUploadCommand(bucket=bucket, key=key, upload_id=upload_id)
        await self._s3_task_queue.abort_multipart_upload(command=command)

    async def generate_part_upload_url(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int,
    ) -> str:
        return await self._provider.generate_part_upload_url(
            bucket=bucket,
            key=key,
            upload_id=upload_id,
            part_number=part_number,
            expires_in=expires_in,
        )

    async def generate_download_url(
        self,
        bucket: str,
        key: str,
        expires_in: int,
    ) -> str:
        return await self._provider.generate_download_url(
            bucket=bucket,
            key=key,
            expires_in=expires_in,
        )

    async def head_object(self, bucket: str, key: str) -> dict:
        return await self._provider.head_object(bucket=bucket, key=key)

    async def get_object(self, bucket: str, key: str, range: str | None = None) -> dict:
        return await self._provider.get_object(bucket=bucket, key=key, range=range)

    async def schedule_delete_object(self, bucket: str, key: str) -> None:
        command = DeleteS3ObjectCommand(bucket=bucket, key=key)
        await self._s3_task_queue.delete_s3_object(command=command)
