from functools import lru_cache

from redis.asyncio import Redis

from app.core.configs import settings


@lru_cache(1)
def get_redis_client(redis_url: str = f'{settings.redis_url}/0') -> Redis:
    return Redis.from_url(url=redis_url, decode_responses=True)
