from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_reactions.commands import DeleteVideoReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.video_reactions.services import IVideoReactionService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.services import IVideoService


@dataclass
class DeleteVideoReactionUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_reaction_service: IVideoReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoReactionCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            self._video_service.ensure_video_access(video=video, channel=channel)

        async with self._transaction_manager:
            await self._video_reaction_service.try_delete_by_video_id_and_channel_id(
                video_id=video.id,
                channel_id=channel.id,
            )
