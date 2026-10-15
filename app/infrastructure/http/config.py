from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx

from app.core.configs import settings


@asynccontextmanager
async def get_httpx_client() -> AsyncGenerator[httpx.AsyncClient]:
    timeout = httpx.Timeout(timeout=settings.http_default_timeout)

    limits = httpx.Limits(
        max_connections=settings.http_max_connections,
        max_keepalive_connections=settings.http_max_keepalive_connections,
        keepalive_expiry=settings.http_keepalive_expiry,
    )

    async with httpx.AsyncClient(timeout=timeout, limits=limits) as client:
        yield client
