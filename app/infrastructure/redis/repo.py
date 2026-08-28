from dataclasses import dataclass
from typing import Any

from redis.asyncio import Redis

from app.domain.common.repos.kv import IKVRepo


@dataclass
class RedisRepo(IKVRepo):
    _redis: Redis

    async def set(self, key: str, value: Any, ttl: int) -> None:
        await self._redis.set(name=key, value=value, ex=ttl)

    async def get(self, key: str) -> Any:
        return await self._redis.get(name=key)

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
