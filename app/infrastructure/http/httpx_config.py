from functools import lru_cache

from httpx import AsyncClient


@lru_cache(1)
def get_httpx_client() -> AsyncClient:
    client = AsyncClient()
    return client
