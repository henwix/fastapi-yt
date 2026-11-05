from abc import ABC, abstractmethod
from uuid import UUID

from app.application.channels.dto import ChannelAboutInfo, DetailedChannel


class IChannelReader(ABC):
    @abstractmethod
    async def try_get_about_info(self, slug: str) -> ChannelAboutInfo: ...

    @abstractmethod
    async def try_get_detailed_by_id(self, id: UUID) -> DetailedChannel: ...
