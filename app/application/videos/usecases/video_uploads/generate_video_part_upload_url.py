from dataclasses import dataclass

from app.application.common.interfaces.s3 import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import GenerateVideoPartUploadUrlCommand
from app.domain.channels.services import IChannelService
from app.domain.files.services import IFileService
from app.domain.videos.exceptions import VideoUploadNotCreatedError
from app.domain.videos.services import IVideoService


@dataclass
class GenerateVideoPartUploadUrlUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _file_service: IFileService
    _s3_service: IS3Service
    _tm: ITransactionManager

    async def execute(self, command: GenerateVideoPartUploadUrlCommand) -> str:
        async with self._tm.begin(commit=False):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            video = await self._video_service.try_get_by_id(id=command.video_id)

            self._video_service.ensure_video_access(video=video, channel=channel)
            self._video_service.ensure_video_upload_not_completed(video=video)
            self._video_service.ensure_video_upload_created(video=video)

            video_file = await self._file_service.get_by_id(id=video.video_file_id)

        if not video_file:
            raise VideoUploadNotCreatedError(video_id=video.id)

        return await self._s3_service.generate_part_upload_url(
            bucket=video_file.bucket,
            key=video_file.key,
            upload_id=video.video_upload_id,
            part_number=command.part_number,
            expires_in=120,
        )
