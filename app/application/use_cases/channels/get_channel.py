from dataclasses import dataclass

from app.application.queries.channels import GetChannelQuery
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService


@dataclass
class GetChannelUseCase:
    channel_service: IChannelService

    async def execute(self, query: GetChannelQuery) -> Channel:
        return await self.channel_service.try_get_active_by_id(id=query.channel_id)
