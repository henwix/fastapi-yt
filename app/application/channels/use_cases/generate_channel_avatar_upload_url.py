from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from app.application.channels.commands import GenerateChannelAvatarUploadUrlCommand
from app.application.common.interfaces.s3.service import IS3Service
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelAvatarInvalidFilenameError
from app.domain.channels.service import IChannelService
from app.domain.common.constants import IMAGE_FILE_MIME_TYPES


@dataclass
class GenerateChannelAvatarUploadUrlUseCase:
    _channel_service: IChannelService
    _s3_service: IS3Service

    async def execute(self, command: GenerateChannelAvatarUploadUrlCommand) -> tuple[str, str, UUID]:
        key_extention = Path(command.filename).suffix.lower()
        if key_extention not in IMAGE_FILE_MIME_TYPES:
            raise ChannelAvatarInvalidFilenameError(filename=command.filename)
        content_type = IMAGE_FILE_MIME_TYPES[key_extention]

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        url, key = await self._s3_service.generate_upload_url(
            bucket=settings.s3_public_bucket_name,
            filename=command.filename,
            content_type=content_type,
            key_prefix=settings.s3_tmp_channel_avatars_key_prefix,
            expires_in=120,
            metadata={'channel_id': str(channel.id)},
        )
        return url, key, channel.id
