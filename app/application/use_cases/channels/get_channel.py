from dataclasses import dataclass

from app.application.queries.channels import GetChannelQuery
from app.domain.channels.entities import Channel
from app.domain.channels.repository import IChannelRepository


@dataclass
class GetChannelUseCase:
    channel_repository: IChannelRepository

    async def execute(self, query: GetChannelQuery) -> Channel:
        return await self.channel_repository.try_get_active_by_id(id=query.channel_id)
