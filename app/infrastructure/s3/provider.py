from dataclasses import dataclass
from uuid import uuid4

from app.application.common.interfaces.s3_provider import IS3Provider
from app.domain.common.exceptions import S3ObjectNotFoundError, S3RequestError
from app.infrastructure.s3.client import BotoS3Client


@dataclass
class BotoS3Provider(IS3Provider):
    _client: BotoS3Client

    def _generate_unique_bucket_key(self, filename: str, key_prefix: str) -> str:
        return f'{key_prefix}/{uuid4().hex[:10]}_{filename}'

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

        async with self._client.client() as s3:
            params: dict = {
                'Bucket': bucket,
                'Key': key,
                'ContentType': content_type,
            }
            if metadata is not None:
                params['Metadata'] = metadata

            url = await s3.generate_presigned_url(
                ClientMethod='put_object',
                Params=params,
                ExpiresIn=expires_in,
            )
        return url, key

    async def head_object(self, bucket: str, key: str) -> dict:
        try:
            async with self._client.client() as s3:
                return await s3.head_object(Bucket=bucket, Key=key)
        except S3RequestError as e:
            status = e.error_status
            match status:
                case 404:
                    raise S3ObjectNotFoundError(key=key) from e
                case _:
                    raise

    async def delete_object(self, bucket: str, key: str) -> dict:
        async with self._client.client() as s3:
            return await s3.delete_object(Bucket=bucket, Key=key)
