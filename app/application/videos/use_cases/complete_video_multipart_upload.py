from dataclasses import dataclass

from app.application.common.interfaces.file_type_detector import IFileTypeDetector
from app.application.common.interfaces.s3.service import IS3Service
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.videos.commands import CompleteVideoMultipartUploadCommand
from app.core.configs import settings
from app.domain.channels.service import IChannelService
from app.domain.videos.constants import VIDEO_FILE_MIME_TYPES
from app.domain.videos.exceptions import VideoInvalidFileContentTypeError
from app.domain.videos.service import IVideoService


@dataclass
class CompleteVideoMultipartUploadUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_service: IS3Service
    _file_type_detector: IFileTypeDetector
    _transaction_manager: ITransactionManager

    async def execute(self, command: CompleteVideoMultipartUploadCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)

        self._video_service.ensure_video_access(video=video, channel=channel)
        self._video_service.ensure_video_upload_not_completed(video=video)

        await self._s3_service.complete_multipart_upload(
            bucket=settings.s3_private_bucket_name,
            key=video.s3_key,
            upload_id=video.upload_id,
            parts=command.parts,
        )

        video_object = await self._s3_service.get_object(
            bucket=settings.s3_private_bucket_name,
            key=video.s3_key,
            range='bytes=0-2047',
        )
        video_metadata_content_type: str = video_object['ContentType']

        video_object_data = await video_object['Body'].read()
        actual_video_mime_type = self._file_type_detector.detect(content=video_object_data)
        print(video_metadata_content_type, actual_video_mime_type)

        if (
            video_metadata_content_type not in VIDEO_FILE_MIME_TYPES.values()
            or actual_video_mime_type not in VIDEO_FILE_MIME_TYPES.values()
        ):
            async with self._transaction_manager:
                await self._video_service.try_delete_by_id(id=video.id)

            await self._s3_service.schedule_delete_object(
                bucket=settings.s3_private_bucket_name,
                key=video.s3_key,
            )
            raise VideoInvalidFileContentTypeError(
                key=video.s3_key,
                metadata_content_type=video_metadata_content_type,
                actual_content_type=actual_video_mime_type,
            )

        video.update_after_completed_upload()
        async with self._transaction_manager:
            await self._video_service.try_update(video=video)
