from dataclasses import dataclass

from app.application.channels.commands import DeleteChannelAvatarCommand
from app.application.common.interfaces.s3_provider import IS3Provider
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.exceptions import ChannelAvatarNotFoundError
from app.domain.channels.services import IChannelService


@dataclass
class DeleteChannelAvatarUseCase:
    channel_service: IChannelService
    transaction_manager: ITransactionManager
    s3_provider: IS3Provider

    async def execute(self, command: DeleteChannelAvatarCommand) -> None:
        async with self.transaction_manager:
            channel = await self.channel_service.try_get_active_by_id(id=command.current_channel_id)

            if channel.avatar_s3_key is None:
                raise ChannelAvatarNotFoundError(channel_id=channel.id)
