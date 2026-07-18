from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.video_reactions.commands import CreateVideoReactionCommand
from app.domain.channels.services import IChannelService
from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_reactions.services import IVideoReactionService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.services import IVideoService


@dataclass
class CreateVideoReactionUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _video_reaction_service: IVideoReactionService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreateVideoReactionCommand) -> tuple[VideoReaction, bool]:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            self._video_service.ensure_video_access(video=video, channel=channel)

        video_reaction = await self._video_reaction_service.get_by_video_id_and_channel_id(
            video_id=video.id,
            channel_id=channel.id,
        )

        async with self._transaction_manager:
            if video_reaction is not None:
                if video_reaction.reaction_type != command.reaction_type:
                    video_reaction.set_reaction_type(reaction_type=command.reaction_type)
                    video_reaction = await self._video_reaction_service.try_update(video_reaction=video_reaction)
                return video_reaction, False

            video_reaction_entity = VideoReaction.create(
                video_id=command.video_id,
                channel_id=command.current_channel_id,
                reaction_type=command.reaction_type,
            )
            new_video_reaction = await self._video_reaction_service.create(video_reaction=video_reaction_entity)
            return new_video_reaction, True
