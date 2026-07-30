from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.playlists.dto import PreviewPlaylistDTO
from app.application.playlists.interfaces.reader import IPlaylistReader
from app.application.playlists.queries import GetPersonalPlaylistsQuery, GetPlaylistsPreviewSortingFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetPersonalPlaylistsUseCase:
    _channel_service: IChannelService
    _playlist_reader: IPlaylistReader

    async def execute(self, query: GetPersonalPlaylistsQuery) -> tuple[list[PreviewPlaylistDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)
                cursor_id_value = UUID(decoded_cursor['id'])

                match query.sorting.sort_by:
                    case GetPlaylistsPreviewSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[GetPlaylistsPreviewSortingFieldsEnum.CREATED_AT.value]
                        )
            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
        playlists = await self._playlist_reader.get_playlists_by_channel_id(
            channel_id=channel.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(playlists) > query.pagination.per_page:
            playlists = playlists[: query.pagination.per_page]
            last_item = playlists[-1]
            next_cursor = {'id': str(last_item.id)}

            match query.sorting.sort_by:
                case GetPlaylistsPreviewSortingFieldsEnum.CREATED_AT:
                    next_cursor[GetPlaylistsPreviewSortingFieldsEnum.CREATED_AT.value] = (
                        last_item.created_at.isoformat()
                    )

        return playlists, base64url_encode(value=next_cursor) if next_cursor is not None else None
