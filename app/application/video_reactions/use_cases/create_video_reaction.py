from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_reactions.commands import CreateVideoReactionCommand
from app.domain.channels.service import IChannelService
from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_reactions.service import IVideoReactionService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.service import IVideoService


@dataclass
class CreateVideoReactionUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_reaction_service: IVideoReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoReactionCommand) -> VideoReaction | None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            self._video_service.ensure_video_access(video=video, channel=channel)

        video_reaction_entity = VideoReaction.create(
            video_id=video.id,
            channel_id=channel.id,
            reaction_type=command.reaction_type,
        )
        async with self._transaction_manager:
            return await self._video_reaction_service.upsert(video_reaction=video_reaction_entity)
