from abc import ABC, abstractmethod
from uuid import UUID

from app.application.common.dto.jwt import JWTTokens


class IAuthService(ABC):
    @abstractmethod
    async def login(self, channel_id: UUID) -> JWTTokens: ...

    @abstractmethod
    async def logout(self, refresh: str) -> None: ...

    @abstractmethod
    async def refresh(self, refresh: str) -> JWTTokens: ...
