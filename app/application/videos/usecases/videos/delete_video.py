from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import DeleteVideoCommand
from app.domain.channels.services import IChannelService
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.services import IVideoService


@dataclass
class DeleteVideoUseCase:
    _video_service: IVideoService
    _channel_service: IChannelService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _tm: ITransactionManager

    async def execute(self, command: DeleteVideoCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            video = await self._video_service.try_get_by_id(id=command.video_id)
            self._video_service.ensure_video_access(video=video, channel=channel)

            cleanups = []

            if video.video_file_id is not None:
                video_file = await self._file_service.get_by_id(id=video.video_file_id)
                if video_file is not None:
                    is_video_file_deleted = await self._file_service.delete_by_id(id=video_file.id)
                    if is_video_file_deleted:
                        cleanups.append(FileCleanup.create(s3_key=video_file.key, bucket=video_file.bucket))
            if video.thumbnail_file_id is not None:
                thumbnail_file = await self._file_service.get_by_id(id=video.thumbnail_file_id)
                if thumbnail_file is not None:
                    is_thumbnail_file_deleted = await self._file_service.delete_by_id(id=thumbnail_file.id)
                    if is_thumbnail_file_deleted:
                        cleanups.append(FileCleanup.create(s3_key=thumbnail_file.key, bucket=thumbnail_file.bucket))

            await self._video_service.try_delete_by_id(id=command.video_id)
            if cleanups:
                await self._file_cleanup_service.upsert_many(cleanups=cleanups)
