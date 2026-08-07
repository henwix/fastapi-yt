from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.video_comments.dto import DetailedVideoCommentDTO
from app.application.video_comments.interfaces.reader import IVideoCommentReader
from app.application.video_comments.queries import GetVideoCommentRepliesQuery, VideoCommentsSortingFieldsEnum
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.domain.video_comments.services import IVideoCommentService
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetVideoCommentRepliesUseCase:
    _video_comment_service: IVideoCommentService
    _video_comment_reader: IVideoCommentReader

    async def execute(self, query: GetVideoCommentRepliesQuery) -> tuple[list[DetailedVideoCommentDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)

                cursor_id_value = UUID(decoded_cursor['id'])

                match query.sorting.sort_by:
                    case VideoCommentsSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[VideoCommentsSortingFieldsEnum.CREATED_AT.value]
                        )

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        video_comment = await self._video_comment_service.try_get_by_id(id=query.video_comment_id)
        replies = await self._video_comment_reader.get_replies(
            video_comment_id=video_comment.id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=query.sorting,
            pagination=query.pagination,
        )

        next_cursor = None

        if len(replies) > query.pagination.per_page:
            replies = replies[: query.pagination.per_page]
            last_item = replies[-1]
            next_cursor = {'id': str(last_item.id)}

            match query.sorting.sort_by:
                case VideoCommentsSortingFieldsEnum.CREATED_AT:
                    next_cursor[VideoCommentsSortingFieldsEnum.CREATED_AT.value] = last_item.created_at.isoformat()

        return replies, base64url_encode(value=next_cursor) if next_cursor else None
