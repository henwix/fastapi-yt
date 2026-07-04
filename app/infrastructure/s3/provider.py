from dataclasses import dataclass
from uuid import uuid4

from botocore.exceptions import BotoCoreError, ClientError

from app.application.common.interfaces.s3_client import IS3Client
from app.application.common.interfaces.s3_provider import IS3Provider
from app.domain.common.exceptions import S3FileNotFoundError, S3RequestError, S3UnavailableError


@dataclass
class BotoS3Provider(IS3Provider):
    _client: IS3Client

    def _generate_unique_bucket_key(self, filename: str, key_prefix: str) -> str:
        return f'{key_prefix}/{uuid4().hex[:10]}_{filename}'

    async def generate_upload_url(
        self,
        bucket: str,
        filename: str,
        key_prefix: str,
        expires_in: int,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        key = self._generate_unique_bucket_key(filename=filename, key_prefix=key_prefix)

        async with self._client.client() as s3:
            params: dict = {
                'Bucket': bucket,
                'Key': key,
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
        async with self._client.client() as s3:
            try:
                return await s3.head_object(Bucket=bucket, Key=key)
            except ClientError as e:
                response = e.response
                status = response['ResponseMetadata']['HTTPStatusCode']

                match status:
                    case 404:
                        raise S3FileNotFoundError(key=key) from e
                    case _:
                        raise S3RequestError(
                            error_code=response['Error']['Code'],
                            error_message=response['Error']['Message'],
                        ) from e
            except BotoCoreError as e:
                raise S3UnavailableError(exc_details=repr(e)) from e
