from dataclasses import dataclass

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.playlists.commands import AddVideoToPlaylistCommand
from app.domain.channels.services import IChannelService
from app.domain.playlists.entities import PlaylistItem
from app.domain.playlists.services import IPlaylistItemService, IPlaylistService
from app.domain.videos.enums import VideoPrivacyStatusEnum
from app.domain.videos.services import IVideoService


@dataclass
class AddVideoToPlaylistUseCase:
    _channel_service: IChannelService
    _playlist_service: IPlaylistService
    _playlist_item_service: IPlaylistItemService
    _video_service: IVideoService
    _transaction_manager: ITransactionManager

    async def execute(self, command: AddVideoToPlaylistCommand) -> None:
        channel = await self._channel_service.try_get_active_by_id(id=command.current_channel_id)
        playlist = await self._playlist_service.try_get_by_id(id=command.playlist_id)

        self._playlist_service.ensure_playlist_access(playlist=playlist, channel=channel)

        video = await self._video_service.try_get_completed_by_id(id=command.video_id)
        if video.privacy_status is VideoPrivacyStatusEnum.PRIVATE:
            self._video_service.ensure_video_access(video=video, channel=channel)

        playlist_item = PlaylistItem.create(playlist_id=playlist.id, video_id=video.id)
        async with self._transaction_manager:
            await self._playlist_item_service.create(playlist_item=playlist_item)
