from abc import ABC, abstractmethod

from app.domain.channels.entities import Channel


class IChannelRepository(ABC):
    @abstractmethod
    async def create(self, channel: Channel) -> Channel: ...

    @abstractmethod
    async def check_channel_exists_by_slug(self, slug: str) -> bool: ...

    @abstractmethod
    async def check_channel_exists_by_email(self, email: str) -> bool: ...
