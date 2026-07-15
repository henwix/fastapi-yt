from dataclasses import dataclass
from uuid import UUID

from app.application.channels.commands import GenerateChannelAvatarUploadURLCommand
from app.application.common.interfaces.s3_provider import IS3Provider
from app.core.configs import settings
from app.domain.channels.services import IChannelService


@dataclass
class GenerateChannelAvatarUploadURLUseCase:
    _channel_service: IChannelService
    _s3_provider: IS3Provider

    async def execute(self, command: GenerateChannelAvatarUploadURLCommand) -> tuple[str, str, UUID]:
        content_type = self._channel_service.validate_channel_avatar_file_format_and_get_content_type(
            value=command.filename
        )

        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        url, key = await self._s3_provider.generate_upload_url(
            bucket=settings.s3_public_bucket_name,
            filename=command.filename,
            content_type=content_type,
            key_prefix=settings.s3_avatars_key_prefix,
            expires_in=120,
            metadata={'channel_id': str(channel.id)},
        )
        return url, key, channel.id
