from abc import ABC, abstractmethod
from uuid import UUID

from app.application.oauth.dto import OAuthAccount


class IOAuthAccountReader(ABC):
    @abstractmethod
    async def get_connected(self, channel_id: UUID) -> list[OAuthAccount]: ...
