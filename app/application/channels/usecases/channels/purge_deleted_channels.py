from dataclasses import dataclass

from app.domain.channels.services import IChannelService


@dataclass
class PurgeDeletedChannelsUseCase:
    _channel_service: IChannelService

    async def execute(self): ...
