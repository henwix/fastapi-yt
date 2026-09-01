from abc import ABC, abstractmethod
from typing import Any


class IHttpClient(ABC):
    @abstractmethod
    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> Any: ...

    @abstractmethod
    async def post(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | None = None,
    ) -> Any: ...
