from dataclasses import dataclass

from app.application.channels.commands import DeleteChannelAvatarCommand
from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.domain.channels.exceptions import ChannelAvatarNotFoundError
from app.domain.channels.services import IChannelService
from app.domain.files.services import IFileService
from app.domain.files_cleanup.entities import FileCleanup
from app.domain.files_cleanup.services import IFileCleanupService


@dataclass
class DeleteChannelAvatarUseCase:
    _channel_service: IChannelService
    _file_service: IFileService
    _file_cleanup_service: IFileCleanupService
    _tm: ITransactionManager

    async def execute(self, command: DeleteChannelAvatarCommand) -> None:
        async with self._tm.begin(commit=True):
            channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
            if channel.avatar_file_id is None:
                raise ChannelAvatarNotFoundError(channel_id=channel.id)

            avatar_file = await self._file_service.get_by_id(id=channel.avatar_file_id)
            if avatar_file is None:
                raise ChannelAvatarNotFoundError(channel_id=channel.id)

            is_avatar_file_deleted = await self._file_service.delete_by_id(id=avatar_file.id)
            if not is_avatar_file_deleted:
                raise ChannelAvatarNotFoundError(channel_id=channel.id)

            avatar_file_cleanup = FileCleanup.create(key=avatar_file.key, bucket=avatar_file.bucket)
            await self._file_cleanup_service.upsert(cleanup=avatar_file_cleanup)
