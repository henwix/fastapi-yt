from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from app.application.common.interfaces.s3.service import IS3Service
from app.application.videos.commands import GenerateVideoThumbnailUploadUrlCommand
from app.core.configs import settings
from app.domain.channels.service import IChannelService
from app.domain.common.constants import IMAGE_FILE_MIME_TYPES
from app.domain.videos.exceptions import VideoThumbnailInvalidFilenameError
from app.domain.videos.service import IVideoService


@dataclass
class GenerateVideoThumbnailUploadUrlUseCase:
    _channel_service: IChannelService
    _video_service: IVideoService
    _s3_service: IS3Service

    async def execute(self, command: GenerateVideoThumbnailUploadUrlCommand) -> tuple[str, str, UUID, str]:
        filename_extension = Path(command.filename).suffix.lower()
        if filename_extension not in IMAGE_FILE_MIME_TYPES:
            raise VideoThumbnailInvalidFilenameError(filename=command.filename)
        content_type = IMAGE_FILE_MIME_TYPES[filename_extension]

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        video = await self._video_service.try_get_by_id(id=command.video_id)
        self._video_service.ensure_video_access(video=video, channel=channel)

        key = self._s3_service.generate_unique_bucket_key(
            filename=command.filename, key_prefix=settings.s3_tmp_video_thumbnails_key_prefix
        )
        url = await self._s3_service.generate_upload_url(
            bucket=settings.s3_public_bucket_name,
            key=key,
            content_type=content_type,
            expires_in=120,
            metadata={
                'channel_id': str(channel.id),
                'video_id': video.id,
            },
        )
        return url, key, channel.id, video.id
