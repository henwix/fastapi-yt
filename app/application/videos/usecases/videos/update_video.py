from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import UpdateVideoCommand
from app.domain.channels.services import IChannelService
from app.domain.videos.entities import Video
from app.domain.videos.services import IVideoService


@dataclass
class UpdateVideoUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _tm: ITransactionManager

    async def execute(self, command: UpdateVideoCommand) -> Video:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            video = await self._video_service.try_get_by_id(id=command.video_id)
            self._video_service.ensure_video_access(video=video, channel=channel)

            video.set_title(value=command.title)
            video.set_description(value=command.description)
            video.set_privacy_status(value=command.privacy_status)
            return await self._video_service.try_update(video=video)
