from functools import lru_cache

from redis.asyncio import Redis

from app.core.configs import settings


@lru_cache(1)
def get_redis_client() -> Redis:
    return Redis.from_url(
        url=f'{settings.redis_url}/0',
        decode_responses=True,
    )
