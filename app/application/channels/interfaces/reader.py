from abc import ABC, abstractmethod

from app.application.channels.dto import ChannelAboutInfoDTO


class IChannelReader(ABC):
    @abstractmethod
    async def try_get_about_info(self, slug: str) -> ChannelAboutInfoDTO: ...
