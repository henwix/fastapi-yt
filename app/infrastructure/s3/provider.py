from dataclasses import dataclass
from uuid import uuid4

from app.application.common.interfaces.s3_provider import IS3Provider
from app.domain.common.exceptions import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3ObjectNotFoundError,
    S3RequestError,
)
from app.infrastructure.s3.client import BotoS3Client


@dataclass
class BotoS3Provider(IS3Provider):
    _client: BotoS3Client

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

        request_params: dict = {
            'Bucket': bucket,
            'Key': key,
            'ContentType': content_type,
        }
        if metadata is not None:
            request_params['Metadata'] = metadata

        async with self._client.client() as s3:
            resp = await s3.create_multipart_upload(**request_params)

        upload_id, key = resp.get('UploadId'), resp.get('Key')
        return upload_id, key

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

        params: dict = {
            'Bucket': bucket,
            'Key': key,
            'ContentType': content_type,
        }
        if metadata is not None:
            params['Metadata'] = metadata

        async with self._client.client() as s3:
            url = await s3.generate_presigned_url(
                ClientMethod='put_object',
                Params=params,
                ExpiresIn=expires_in,
            )
        return url, key

    async def complete_multipart_upload(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        parts: list[dict],
    ) -> dict:
        try:
            async with self._client.client() as s3:
                return await s3.complete_multipart_upload(
                    Bucket=bucket,
                    Key=key,
                    UploadId=upload_id,
                    MultipartUpload={'Parts': parts},
                )
        except S3RequestError as e:
            if e.error_status == 400 and e.error_code == 'InvalidPart':
                raise S3MultipartUploadInvalidPartsError(bucket=bucket, key=key, upload_id=upload_id)
            elif e.error_status == 404 and e.error_code == 'NoSuchUpload':
                raise S3MultipartUploadNotFoundError(bucket=bucket, key=key, upload_id=upload_id)
            else:
                raise

    async def abort_multipart_upload(self, bucket: str, key: str, upload_id: str) -> dict:
        try:
            async with self._client.client() as s3:
                return await s3.abort_multipart_upload(Bucket=bucket, Key=key, UploadId=upload_id)
        except S3RequestError as e:
            match e.error_status:
                case 404:
                    raise S3MultipartUploadNotFoundError(bucket=bucket, key=key, upload_id=upload_id)
                case _:
                    raise

    async def generate_part_upload_url(
        self,
        bucket: str,
        key: str,
        upload_id: str,
        part_number: int,
        expires_in: int,
    ) -> str:
        async with self._client.client() as s3:
            return await s3.generate_presigned_url(
                ClientMethod='upload_part',
                Params={
                    'Bucket': bucket,
                    'Key': key,
                    'UploadId': upload_id,
                    'PartNumber': part_number,
                },
                ExpiresIn=expires_in,
            )

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
