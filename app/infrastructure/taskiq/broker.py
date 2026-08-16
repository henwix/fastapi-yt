from functools import lru_cache

from taskiq.middlewares import SmartRetryMiddleware
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.core.configs import settings


@lru_cache(1)
def get_broker() -> RedisStreamBroker:
    result_backend = RedisAsyncResultBackend(
        redis_url=f'{settings.redis_url}/1',
        result_ex_time=1000,
    )

    broker = (
        RedisStreamBroker(
            url=f'{settings.redis_url}/2',
        )
        .with_result_backend(result_backend=result_backend)
        .with_middlewares(SmartRetryMiddleware())
    )
    return broker
