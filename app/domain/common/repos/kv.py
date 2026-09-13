from abc import ABC, abstractmethod


class IKVRepo(ABC):
    @abstractmethod
    async def set(self, key: str, value: str | bytes | int | float, ttl_seconds: int) -> None: ...

    @abstractmethod
    async def get(self, key: str) -> str | bytes | None: ...

    @abstractmethod
    async def delete(self, key: str) -> bool: ...
