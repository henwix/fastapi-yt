from dataclasses import dataclass

from app.application.common.interfaces.task_queue import ITaskQueue
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import DeleteVideoCommand
from app.core.configs import settings
from app.domain.channels.services import IChannelService
from app.domain.videos.services import IVideoService


@dataclass
class DeleteVideoUseCase:
    _video_service: IVideoService
    _channel_service: IChannelService
    _transaction_manager: ITransactionManager
    _task_queue: ITaskQueue

    async def execute(self, command: DeleteVideoCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_completed_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)

        async with self._transaction_manager:
            await self._video_service.try_delete_by_id(id=command.video_id)

        await self._task_queue.delete_s3_object(bucket=settings.s3_private_bucket_name, key=video.s3_key)
