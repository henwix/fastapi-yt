from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import DeleteVideoCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService
from app.domain.videos.services import IVideoService


@dataclass
class DeleteVideoUseCase:
    _video_service: IVideoService
    _channel_service: IChannelService
    _file_cleanup_service: IFileCleanupService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoCommand) -> None:
        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)

        cleanups = []
        if video.s3_key is not None:
            cleanups.append(FileCleanup.create(s3_key=video.s3_key, bucket=settings.s3_private_bucket_name))
        if video.thumbnail_s3_key is not None:
            cleanups.append(FileCleanup.create(s3_key=video.thumbnail_s3_key, bucket=settings.s3_public_bucket_name))

        async with self._transaction_manager:
            await self._video_service.try_delete_by_id(id=command.video_id)
            if cleanups:
                await self._file_cleanup_service.create_many(cleanups=cleanups)
