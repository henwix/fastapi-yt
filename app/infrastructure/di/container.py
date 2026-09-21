from functools import lru_cache

from dishka import AsyncContainer, make_async_container

from app.infrastructure.di.providers import get_providers


@lru_cache(1)
def get_container() -> AsyncContainer:
    return make_async_container(*get_providers())
