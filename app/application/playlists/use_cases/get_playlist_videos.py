from dataclasses import dataclass
from datetime import datetime

from app.application.playlists.dto import PlaylistPreviewVideoDTO
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.application.playlists.queries import GetPlaylistVideosQuery, PlaylistVideosSortingFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.playlists.exceptions import PlaylistAccessForbiddenError
from app.domain.playlists.services import IPlaylistService
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetPlaylistVideosUseCase:
    _channel_service: IChannelService
    _playlist_service: IPlaylistService
    _playlist_reader: IPlaylistReader

    async def execute(self, query: GetPlaylistVideosQuery) -> tuple[list[PlaylistPreviewVideoDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)
                cursor_id_value = decoded_cursor['id']

                match query.sorting.sort_by:
                    case PlaylistVideosSortingFieldsEnum.ADDED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[PlaylistVideosSortingFieldsEnum.ADDED_AT.value]
                        )
                    case PlaylistVideosSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[PlaylistVideosSortingFieldsEnum.CREATED_AT.value]
                        )
                    case PlaylistVideosSortingFieldsEnum.POPULAR:
                        cursor_sort_value = int(decoded_cursor[PlaylistVideosSortingFieldsEnum.POPULAR.value])

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        playlist = await self._playlist_service.try_get_by_id(id=query.playlist_id)

        if playlist.privacy_status is PlaylistPrivacyStatusEnum.PRIVATE:
            if query.current_channel_id is None:
                raise PlaylistAccessForbiddenError(playlist_id=query.playlist_id, channel_id=None)

            channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
            self._playlist_service.ensure_playlist_access(playlist=playlist, channel=channel)

        playlist_videos = await self._playlist_reader.get_playlist_videos_by_playlist_id(
            playlist_id=playlist.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(playlist_videos) > query.pagination.per_page:
            playlist_videos = playlist_videos[: query.pagination.per_page]
            last_item = playlist_videos[-1]
            next_cursor = {'id': last_item.id}

            match query.sorting.sort_by:
                case PlaylistVideosSortingFieldsEnum.ADDED_AT:
                    next_cursor[PlaylistVideosSortingFieldsEnum.ADDED_AT.value] = last_item.added_at.isoformat()
                case PlaylistVideosSortingFieldsEnum.CREATED_AT:
                    next_cursor[PlaylistVideosSortingFieldsEnum.CREATED_AT.value] = last_item.created_at.isoformat()
                case PlaylistVideosSortingFieldsEnum.POPULAR:
                    next_cursor[PlaylistVideosSortingFieldsEnum.POPULAR.value] = str(last_item.views_count)

        return playlist_videos, base64url_encode(value=next_cursor) if next_cursor is not None else None
