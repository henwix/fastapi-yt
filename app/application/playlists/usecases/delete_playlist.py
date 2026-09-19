from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.playlists.commands import DeletePlaylistCommand
from app.domain.channels.services import IChannelService
from app.domain.playlists.services import IPlaylistService


@dataclass
class DeletePlaylistUseCase:
    _channel_service: IChannelService
    _playlist_service: IPlaylistService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeletePlaylistCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        playlist = await self._playlist_service.try_get_by_id(id=command.playlist_id)
        self._playlist_service.ensure_playlist_access(playlist=playlist, channel=channel)
        async with self._transaction_manager:
            await self._playlist_service.try_delete_by_id(id=playlist.id)
