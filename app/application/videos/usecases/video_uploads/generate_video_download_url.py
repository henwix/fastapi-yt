from dataclasses import dataclass

from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import GenerateVideoDownloadUrlCommand
from app.domain.channels.services import IChannelService
from app.domain.files.services import IFileService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoFileNotFoundError
from app.domain.videos.services import IVideoService


@dataclass
class GenerateVideoDownloadUrlUseCase:
    _video_service: IVideoService
    _channel_service: IChannelService
    _file_service: IFileService
    _s3_service: IS3Service
    _tm: ITransactionManager

    async def execute(self, command: GenerateVideoDownloadUrlCommand) -> str:
        async with self._tm.begin(commit=False):
            video = await self._video_service.try_get_completed_by_id(id=command.video_id)

            if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
                if command.current_channel_id is None:
                    raise VideoAccessForbiddenError(video_id=video.id)
                channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
                self._video_service.ensure_video_access(video=video, channel=channel)

        if video.video_file_id is None:
            raise VideoFileNotFoundError(video_id=video.id)

        video_file = await self._file_service.get_by_id(id=video.video_file_id)
        if video_file is None:
            raise VideoFileNotFoundError(video_id=video.id)

        return await self._s3_service.generate_download_url(
            bucket=video_file.bucket,
            key=video_file.key,
            expires_in=10800,
        )
