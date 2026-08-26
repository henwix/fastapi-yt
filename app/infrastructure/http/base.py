from abc import ABC, abstractmethod


class IHttpClient(ABC):
    @abstractmethod
    async def get(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
    ) -> dict: ...

    @abstractmethod
    async def post(
        self,
        url: str,
        params: dict | None = None,
        headers: dict | None = None,
        data: dict | None = None,
    ) -> dict: ...
