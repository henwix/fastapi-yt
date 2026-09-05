from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import aioboto3
from aiobotocore.config import AioConfig
from types_aiobotocore_s3 import S3Client

from app.core.configs import settings


@asynccontextmanager
async def get_s3_client() -> AsyncGenerator[S3Client]:
    config = AioConfig(
        connect_timeout=5,
        read_timeout=10,
    )
    session = aioboto3.Session()
    async with session.client(
        config=config,
        service_name='s3',
        region_name='auto',
        endpoint_url=settings.s3_endpoint,
        aws_access_key_id=settings.s3_access_key,
        aws_secret_access_key=settings.s3_secret_key,
    ) as s3:
        yield s3
