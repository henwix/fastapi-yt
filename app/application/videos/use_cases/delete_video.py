from dataclasses import dataclass

from app.application.common.commands.s3 import DeleteS3ObjectCommand
from app.application.common.interfaces.task_queues.s3 import IS3TaskQueue
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
    _s3_task_queue: IS3TaskQueue

    async def execute(self, command: DeleteVideoCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_completed_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)

        async with self._transaction_manager:
            await self._video_service.try_delete_by_id(id=command.video_id)

        delete_s3_object_command = DeleteS3ObjectCommand(bucket=settings.s3_private_bucket_name, key=video.s3_key)
        await self._s3_task_queue.delete_s3_object(command=delete_s3_object_command)
