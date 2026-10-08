from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.playlists.commands import DeleteVideoFromPlaylistCommand
from app.domain.channels.services import IChannelService
from app.domain.playlists.services import IPlaylistItemService, IPlaylistService


@dataclass
class DeleteVideoFromPlaylistUseCase:
    _channel_service: IChannelService
    _playlist_service: IPlaylistService
    _playlist_item_service: IPlaylistItemService
    _transaction_manager: ITransactionManager

    async def execute(self, command: DeleteVideoFromPlaylistCommand) -> None:
        channel = await self._channel_service.try_get_existing_by_id_for_auth(id=command.current_channel_id)
        playlist = await self._playlist_service.try_get_existing_by_id(id=command.playlist_id)

        self._playlist_service.ensure_playlist_access(playlist=playlist, channel=channel)

        async with self._transaction_manager:
            await self._playlist_item_service.try_delete(playlist_id=playlist.id, video_id=command.video_id)
