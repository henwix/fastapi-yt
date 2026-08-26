from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.video_comments.dto import DetailedVideoCommentDTO
from app.application.video_comments.interfaces.reader import IVideoCommentReader
from app.application.video_comments.queries import GetVideoCommentsQuery, VideoCommentsSortingFieldsEnum
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.domain.videos.service import IVideoService
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetVideoCommentsUseCase:
    _video_service: IVideoService
    _video_comment_reader: IVideoCommentReader

    async def execute(self, query: GetVideoCommentsQuery) -> tuple[list[DetailedVideoCommentDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor: dict[str, str] = base64url_decode(value=query.pagination.cursor)

                cursor_id_value = UUID(decoded_cursor['id'])

                match query.sorting.sort_by:
                    case VideoCommentsSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[VideoCommentsSortingFieldsEnum.CREATED_AT.value]
                        )

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        video = await self._video_service.try_get_completed_by_id(id=query.video_id)
        comments = await self._video_comment_reader.get_comments(
            video_id=video.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(comments) > query.pagination.per_page:
            comments = comments[: query.pagination.per_page]
            last_item = comments[-1]
            next_cursor = {'id': str(last_item.id)}

            match query.sorting.sort_by:
                case VideoCommentsSortingFieldsEnum.CREATED_AT:
                    next_cursor[VideoCommentsSortingFieldsEnum.CREATED_AT.value] = last_item.created_at.isoformat()

        return comments, base64url_encode(value=next_cursor) if next_cursor else None
