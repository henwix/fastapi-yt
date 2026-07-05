from taskiq.middlewares import SmartRetryMiddleware
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from app.core.configs import settings

result_backend = RedisAsyncResultBackend(
    redis_url=settings.redis_url,
    result_ex_time=1000,
)

broker = (
    RedisStreamBroker(
        url=settings.redis_url,
    )
    .with_result_backend(result_backend=result_backend)
    .with_middlewares(SmartRetryMiddleware())
)
