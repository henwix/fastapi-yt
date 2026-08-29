from functools import lru_cache

import httpx

from app.core.configs import settings


@lru_cache(1)
def get_httpx_client() -> httpx.AsyncClient:
    timeout = httpx.Timeout(timeout=settings.http_default_timeout)

    limits = httpx.Limits(
        max_connections=settings.http_max_connections,
        max_keepalive_connections=settings.http_max_keepalive_connections,
        keepalive_expiry=settings.http_keepalive_expiry,
    )

    client = httpx.AsyncClient(timeout=timeout, limits=limits)
    return client
