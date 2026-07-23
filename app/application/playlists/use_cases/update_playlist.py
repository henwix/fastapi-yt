from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.playlists.commands import UpdatePlaylistCommand
from app.domain.channels.services import IChannelService
from app.domain.playlists.entities import Playlist
from app.domain.playlists.services import IPlaylistService


@dataclass
class UpdatePlaylistUseCase:
    _channel_service: IChannelService
    _playlist_service: IPlaylistService
    _transaction_manager: ITransactionManager

    async def execute(self, command: UpdatePlaylistCommand) -> Playlist:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        playlist = await self._playlist_service.try_get_by_id(id=command.playlist_id)
        self._playlist_service.ensure_playlist_access(playlist=playlist, channel=channel)

        playlist.update(
            title=command.title,
            description=command.description,
            privacy_status=command.privacy_status,
        )
        async with self._transaction_manager:
            return await self._playlist_service.try_update(playlist=playlist)
