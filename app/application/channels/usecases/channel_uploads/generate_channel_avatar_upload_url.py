from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from app.application.channels.commands import GenerateChannelAvatarUploadUrlCommand
from app.application.common.interfaces.s3 import IS3Service
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelAvatarInvalidFilenameError
from app.domain.channels.services import IChannelService
from app.domain.common.constants import IMAGE_FILE_MIME_TYPES
from app.domain.common.repos.kv import IKVRepo


@dataclass
class GenerateChannelAvatarUploadUrlUseCase:
    _channel_service: IChannelService
    _s3_service: IS3Service
    _kv_repo: IKVRepo

    async def execute(self, command: GenerateChannelAvatarUploadUrlCommand) -> tuple[str, str, UUID]:
        filename_extension = Path(command.filename).suffix.lower()
        if filename_extension not in IMAGE_FILE_MIME_TYPES:
            raise ChannelAvatarInvalidFilenameError(filename=command.filename)
        content_type = IMAGE_FILE_MIME_TYPES[filename_extension]

        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)

        avatar_upload_url_ttl = 120
        key = self._s3_service.generate_unique_bucket_key(
            filename=command.filename, key_prefix=settings.s3_tmp_channel_avatars_key_prefix
        )
        bucket_name = settings.s3_public_bucket_name
        url = await self._s3_service.generate_upload_url(
            bucket=bucket_name,
            key=key,
            content_type=content_type,
            expires_in=avatar_upload_url_ttl,
            metadata={'channel_id': str(channel.id)},
        )
        await self._kv_repo.set(
            key=f'set_channel_avatar_url:{bucket_name}:{key}', value='', ttl_seconds=avatar_upload_url_ttl
        )
        return url, key, channel.id
