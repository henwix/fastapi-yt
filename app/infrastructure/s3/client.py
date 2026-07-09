from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from aioboto3 import Session
from aiobotocore.config import AioConfig
from botocore.exceptions import BotoCoreError, ClientError
from types_aiobotocore_s3.client import S3Client

from app.core.configs import settings
from app.domain.common.exceptions import S3RequestError, S3UnavailableError


class BotoS3Client:
    def __init__(self) -> None:
        self._config = AioConfig(
            connect_timeout=5,
            read_timeout=10,
        )
        self._session = Session()

    @asynccontextmanager
    async def client(self) -> AsyncGenerator[S3Client]:
        async with self._session.client(
            config=self._config,
            service_name='s3',
            region_name='auto',
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        ) as s3:
            try:
                yield s3
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
