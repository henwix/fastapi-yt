from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.playlists.commands import CreatePlaylistCommand
from app.domain.channels.services import IChannelService
from app.domain.playlists.entities import Playlist
from app.domain.playlists.services import IPlaylistService


@dataclass
class CreatePlaylistUseCase:
    _channel_service: IChannelService
    _playlist_service: IPlaylistService
    _transaction_manager: ITransactionManager

    async def execute(self, command: CreatePlaylistCommand) -> Playlist:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)

        playlist_entity = Playlist.create(
            title=command.title,
            description=command.description,
            privacy_status=command.privacy_status,
            channel_id=channel.id,
        )
        async with self._transaction_manager:
            return await self._playlist_service.create(playlist=playlist_entity)
