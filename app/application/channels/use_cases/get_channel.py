from dataclasses import dataclass

from app.application.channels.queries import GetChannelQuery
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService


@dataclass
class GetChannelUseCase:
    _channel_service: IChannelService

    async def execute(self, query: GetChannelQuery) -> Channel:
        return await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
