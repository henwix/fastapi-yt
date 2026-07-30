from dataclasses import dataclass

from app.application.playlists.dto import DetailedPlaylistDTO
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.application.playlists.queries import GetPlaylistQuery
from app.domain.channels.services import IChannelService
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.playlists.exceptions import PlaylistAccessForbiddenError


@dataclass
class GetPlaylistUseCase:
    _playlist_reader: IPlaylistReader
    _channel_service: IChannelService

    async def execute(self, query: GetPlaylistQuery) -> DetailedPlaylistDTO:
        playlist = await self._playlist_reader.try_get_detailed_playlist_by_id(id=query.playlist_id)

        if playlist.privacy_status is PlaylistPrivacyStatusEnum.PRIVATE:
            if query.current_channel_id is None:
                raise PlaylistAccessForbiddenError(playlist_id=playlist.id, channel_id=None)

            channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)

            if channel.slug != playlist.author_slug:
                raise PlaylistAccessForbiddenError(playlist_id=playlist.id, channel_id=channel.id)

        return playlist
