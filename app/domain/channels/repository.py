from abc import ABC, abstractmethod

from app.domain.channels.entities import Channel


class IChannelRepository(ABC):
    @abstractmethod
    async def create(self, channel: Channel) -> Channel: ...

    @abstractmethod
    async def check_channel_exists_by_slug(self, slug: str) -> bool: ...

    @abstractmethod
    async def check_channel_exists_by_email(self, email: str) -> bool: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Channel | None: ...

    @abstractmethod
    async def try_get_active_by_id(self, id: int) -> Channel: ...

    @abstractmethod
    async def update(self, channel: Channel) -> Channel: ...

    @abstractmethod
    async def try_delete_by_id(self, id: int) -> bool: ...
