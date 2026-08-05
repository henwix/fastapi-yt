from dataclasses import dataclass
from datetime import datetime

from app.application.video_history.dto import PreviewVideoHistoryDTO
from app.application.video_history.interfaces.reader import IVideoHistoryReader
from app.application.video_history.queries import GetVideoHistoryQuery, VideoHistorySortingFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetVideoHistoryUseCase:
    _channel_service: IChannelService
    _video_history_reader: IVideoHistoryReader

    async def execute(self, query: GetVideoHistoryQuery) -> tuple[list[PreviewVideoHistoryDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)
                cursor_id_value = decoded_cursor['id']

                match query.sorting.sort_by:
                    case VideoHistorySortingFieldsEnum.WATCHED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[VideoHistorySortingFieldsEnum.WATCHED_AT.value]
                        )
            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        channel = await self._channel_service.try_get_active_by_id(id=query.current_channel_id)
        history_videos = await self._video_history_reader.get_many(
            channel_id=channel.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(history_videos) > query.pagination.per_page:
            history_videos = history_videos[: query.pagination.per_page]
            last_item = history_videos[-1]
            next_cursor = {'id': last_item.id}

            match query.sorting.sort_by:
                case VideoHistorySortingFieldsEnum.WATCHED_AT:
                    next_cursor[VideoHistorySortingFieldsEnum.WATCHED_AT.value] = last_item.watched_at.isoformat()

        return history_videos, base64url_encode(value=next_cursor) if next_cursor is not None else None
