from dataclasses import dataclass
from datetime import datetime

from app.application.videos.dto import PersonalVideoDTO
from app.application.videos.interfaces.reader import IVideoReader
from app.application.videos.queries import GetPersonalVideosQuery, GetPersonalVideosSortingFieldEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetPersonalVideosUseCase:
    _channel_service: IChannelService
    _video_reader: IVideoReader

    async def execute(self, query: GetPersonalVideosQuery) -> tuple[list[PersonalVideoDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)

                cursor_id_value = decoded_cursor['id']

                match query.sorting.sort_by:
                    case GetPersonalVideosSortingFieldEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[GetPersonalVideosSortingFieldEnum.CREATED_AT.value]
                        )

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e))

        channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
        videos = await self._video_reader.get_personal_videos(
            channel_id=channel.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            filters=query.filters,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(videos) > query.pagination.per_page:
            videos = videos[: query.pagination.per_page]
            last_item = videos[-1]
            next_cursor = {'id': str(last_item.id)}

            match query.sorting.sort_by:
                case GetPersonalVideosSortingFieldEnum.CREATED_AT:
                    next_cursor[GetPersonalVideosSortingFieldEnum.CREATED_AT.value] = last_item.created_at.isoformat()

        return videos, base64url_encode(value=next_cursor) if next_cursor is not None else None
