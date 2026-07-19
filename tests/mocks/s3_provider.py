from uuid import UUID, uuid7

from app.infrastructure.s3.client import BotoS3Client
from app.infrastructure.s3.provider import BotoS3Provider


class DummyS3Provider(BotoS3Provider):
    def __init__(self, _client: BotoS3Client):
        super().__init__(_client=_client)
        self.METADATA_CHANNEL_ID: UUID = uuid7()
        self.CONTENT_TYPE: str = 'image/png'

    async def head_object(self, bucket: str, key: str) -> dict:
        return {'Metadata': {'channel_id': str(self.METADATA_CHANNEL_ID)}, 'ContentType': self.CONTENT_TYPE}
