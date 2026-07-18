from dataclasses import dataclass

from app.application.videos.dto import DetailedVideoDTO
from app.application.videos.interfaces.reader import IVideoReader
from app.application.videos.queries import GetVideoQuery
from app.domain.channels.services import IChannelService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError
from app.domain.videos.services import IVideoService


@dataclass
class GetVideoUseCase:
    _video_service: IVideoService
    _video_reader: IVideoReader
    _channel_service: IChannelService

    async def execute(self, query: GetVideoQuery) -> DetailedVideoDTO:
        video = await self._video_reader.try_get_detailed_by_id(id=query.video_id)

        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            if query.current_channel_id is None:
                raise VideoAccessForbiddenError(video_id=video.id)

            channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)

            if video.channel_id != channel.id:
                raise VideoAccessForbiddenError(video_id=video.id, channel_id=channel.id)

        return video
