from uuid import UUID, uuid4, uuid7

from types_aiobotocore_s3.client import S3Client

from app.infrastructure.s3.provider import BotoS3Provider


class MockS3Provider(BotoS3Provider):
    def __init__(self, _s3_client: S3Client):
        super().__init__(_s3_client=_s3_client)
        self.METADATA_CHANNEL_ID: UUID = uuid7()
        self.CONTENT_TYPE: str = 'image/png'
        self.CONTENT_LENGTH: int = 1048576
        self.UPLOAD_ID: str = uuid4().hex

    async def head_object(self, bucket: str, key: str) -> dict:
        return {
            'Metadata': {'channel_id': str(self.METADATA_CHANNEL_ID)},
            'ContentType': self.CONTENT_TYPE,
            'ContentLength': self.CONTENT_LENGTH,
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
