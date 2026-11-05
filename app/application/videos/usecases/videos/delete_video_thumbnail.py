from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import DeleteVideoThumbnailCommand
from app.domain.channels.services import IChannelService
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.exceptions import VideoThumbnailNotFoundError
from app.domain.videos.services import IVideoService


@dataclass
class DeleteVideoThumbnailUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _tm: ITransactionManager

    async def execute(self, command: DeleteVideoThumbnailCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            video = await self._video_service.try_get_by_id(id=command.video_id)
            self._video_service.ensure_video_access(video=video, channel=channel)
            if video.thumbnail_file_id is None:
                raise VideoThumbnailNotFoundError(video_id=video.id)

            thumbnail_file = await self._file_service.get_by_id(id=video.thumbnail_file_id)
            if thumbnail_file is None:
                raise VideoThumbnailNotFoundError(video_id=video.id)

            is_thumbnail_file_deleted = await self._file_service.delete_by_id(id=thumbnail_file.id)
            if not is_thumbnail_file_deleted:
                raise VideoThumbnailNotFoundError(video_id=video.id)

            thumbnail_file_cleanup = FileCleanup.create(key=thumbnail_file.key, bucket=thumbnail_file.bucket)
            await self._file_cleanup_service.upsert(cleanup=thumbnail_file_cleanup)
