from dataclasses import dataclass

from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import AbortVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.videos.services import IVideoService


@dataclass
class AbortVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _task_queue: ITaskQueue
    _transaction_manager: ITransactionManager

    async def execute(self, command: AbortVideoMultipartUploadCommand) -> None:
        self._video_service.validate_video_file_format_and_get_content_type(value=command.key)
        self._video_service.validate_video_key(key=command.key, key_prefix=settings.s3_videos_key_prefix)

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_upload_id_and_s3_key(
            upload_id=command.upload_id, s3_key=command.key
        )
        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        async with self._transaction_manager:
            await self._video_service.try_delete_by_id(id=video.id)

        await self._task_queue.abort_multipart_upload(
            bucket=settings.s3_private_bucket_name,
            key=command.key,
            upload_id=command.upload_id,
        )
