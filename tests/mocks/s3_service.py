import secrets
from uuid import UUID, uuid7

from app.application.common.interfaces.s3.provider import IS3Provider
from app.application.common.interfaces.task_queues.s3 import IS3TaskQueue
from app.infrastructure.s3.service import S3Service


class MockS3Service(S3Service):
    def __init__(self, _provider: IS3Provider, _s3_task_queue: IS3TaskQueue):
        super().__init__(_provider=_provider, _s3_task_queue=_s3_task_queue)
        self.METADATA_CHANNEL_ID: UUID = uuid7()
        self.CONTENT_TYPE: str = 'image/png'
        self.CONTENT_LENGTH: int = 1024 * 1024 * 1
        self.UPLOAD_ID: str = secrets.token_hex(16)

    def _generate_unique_bucket_key(self, filename: str, key_prefix: str) -> str:
        return f'{key_prefix}/{secrets.token_hex(5)}_{filename}'

    async def get_object(self, bucket: str, key: str, range: str | None = None) -> dict:
        class DummyObjectBody:
            async def read(self) -> None:
                return

        return {
            'Metadata': {'channel_id': str(self.METADATA_CHANNEL_ID)},
            'ContentType': self.CONTENT_TYPE,
            'ContentLength': self.CONTENT_LENGTH,
            'Body': DummyObjectBody(),
        }

    async def create_multipart_upload(
        self,
        bucket: str,
        filename: str,
        content_type: str,
        key_prefix: str,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        key = self._generate_unique_bucket_key(filename=filename, key_prefix=key_prefix)
        return self.UPLOAD_ID, key

    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[dict],
    ) -> dict:
        return {}

    async def schedule_delete_object(self, bucket: str, key: str) -> None:
        return

    async def schedule_abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> None:
        return

    async def copy_object(self, bucket: str, current_key: str, new_key: str) -> None:
        return
