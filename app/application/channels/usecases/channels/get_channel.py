from dataclasses import dataclass

from app.application.channels.dto import DetailedChannel
from app.application.channels.interfaces import IChannelReader
from app.application.channels.queries import GetChannelQuery


@dataclass
class GetChannelUseCase:
    _channel_reader: IChannelReader

    async def execute(self, query: GetChannelQuery) -> DetailedChannel:
        return await self._channel_reader.try_get_detailed_by_id(id=query.current_channel_id)
