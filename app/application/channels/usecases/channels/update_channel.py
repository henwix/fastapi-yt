from dataclasses import dataclass

from app.application.channels.commands import UpdateChannelCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.entities import Channel
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty


@dataclass
class UpdateChannelUseCase:
    _channel_service: IChannelService
    _tm: ITransactionManager

    async def execute(self, command: UpdateChannelCommand) -> Channel:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            if command.slug is not Empty.UNSET:
                await self._channel_service.try_check_slug_exists(slug=command.slug)

            channel.set_name(value=command.name)
            channel.set_slug(value=command.slug)
            channel.set_description(value=command.description)
            channel.set_country(value=command.country)

            return await self._channel_service.try_update(channel=channel)
