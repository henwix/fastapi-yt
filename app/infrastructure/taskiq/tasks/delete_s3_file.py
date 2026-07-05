import asyncio
from uuid import UUID

from app.infrastructure.taskiq.config import broker


@broker.task(retry_on_error=True, max_retries=10, delay=15)
async def delete_s3_file(a: UUID, b: str) -> None:
    print(f'start sleep with params: a={a}, b={b}')
    await asyncio.sleep(5)
    raise ValueError('assdd')
    print(f'end sleep with params: a={a}, b={b}')
