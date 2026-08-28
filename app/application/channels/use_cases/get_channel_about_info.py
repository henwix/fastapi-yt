from dataclasses import dataclass

from app.application.channels.dto import ChannelAboutInfo
from app.application.channels.interfaces.reader import IChannelReader
from app.application.channels.queries import GetChannelAboutInfoQuery


@dataclass
class GetChannelAboutInfoUseCase:
    _reader: IChannelReader

    async def execute(self, query: GetChannelAboutInfoQuery) -> ChannelAboutInfo:
        return await self._reader.try_get_about_info(slug=query.channel_slug)
