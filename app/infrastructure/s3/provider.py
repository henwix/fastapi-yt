from dataclasses import dataclass
from typing import Any

from botocore.exceptions import BotoCoreError, ClientError
from types_aiobotocore_s3.client import S3Client
from types_aiobotocore_s3.type_defs import CreateMultipartUploadOutputTypeDef

from app.application.common.interfaces.s3.provider import IS3Provider
from app.domain.common.exceptions import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3UnavailableError,
)


@dataclass
class BotoS3Provider(IS3Provider):
    _s3_client: S3Client

    async def _client_action(self, method, **kwargs) -> Any:
        try:
            return await method(**kwargs)
        except ClientError as e:
            response = e.response
            status = response.get('ResponseMetadata', {}).get('HTTPStatusCode')
            raise S3RequestError(
                error_code=response.get('Error', {}).get('Code'),
                error_message=response.get('Error', {}).get('Message'),
                error_status=status,
            ) from e
        except BotoCoreError as e:
            raise S3UnavailableError(exc_details=repr(e)) from e

    async def create_multipart_upload(
        self,
        bucket: str,
        key: str,
        content_type: str,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        request_params: dict = {
            'Bucket': bucket,
            'Key': key,
            'ContentType': content_type,
        }
        if metadata is not None:
            request_params['Metadata'] = metadata

        resp: CreateMultipartUploadOutputTypeDef = await self._client_action(
            self._s3_client.create_multipart_upload,
            **request_params,
        )

        upload_id, key = resp.get('UploadId'), resp.get('Key')
        return upload_id, key

    async def generate_upload_url(
        self,
        bucket: str,
        key: str,
        content_type: str,
        expires_in: int,
        metadata: dict[str, str] | None = None,
    ) -> tuple[str, str]:
        params: dict = {
            'Bucket': bucket,
            'Key': key,
            'ContentType': content_type,
        }
        if metadata is not None:
            params['Metadata'] = metadata

        url: str = await self._client_action(
            self._s3_client.generate_presigned_url,
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
            return await self._client_action(
                self._s3_client.complete_multipart_upload,
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
            return await self._client_action(
                self._s3_client.abort_multipart_upload,
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
            )
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
        return await self._client_action(
            self._s3_client.generate_presigned_url,
            ClientMethod='upload_part',
            Params={
                'Bucket': bucket,
                'Key': key,
                'UploadId': upload_id,
                'PartNumber': part_number,
            },
            ExpiresIn=expires_in,
        )

    async def generate_download_url(self, bucket: str, key: str, expires_in: int) -> str:
        return await self._client_action(
            self._s3_client.generate_presigned_url,
            ClientMethod='get_object',
            Params={'Bucket': bucket, 'Key': key},
            ExpiresIn=expires_in,
        )

    async def head_object(self, bucket: str, key: str) -> dict:
        try:
            return await self._client_action(
                self._s3_client.head_object,
                Bucket=bucket,
                Key=key,
            )
        except S3RequestError as e:
            status = e.error_status
            match status:
                case 404:
                    raise S3ObjectNotFoundError(key=key) from e
                case _:
                    raise

    async def get_object(self, bucket: str, key: str, range: str | None = None) -> dict:
        try:
            return await self._client_action(
                self._s3_client.get_object,
                Bucket=bucket,
                Key=key,
            )
        except S3RequestError as e:
            status = e.error_status
            match status:
                case 404:
                    raise S3ObjectNotFoundError(key=key) from e
                case _:
                    raise

    async def delete_object(self, bucket: str, key: str) -> dict:
        return await self._client_action(
            self._s3_client.delete_object,
            Bucket=bucket,
            Key=key,
        )
