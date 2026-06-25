from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comments.dto import DetailedPostCommentDTO
from app.application.post_comments.interfaces.reader import IPostCommentReader
from app.application.post_comments.queries import GetPostCommentRepliesQuery, PostCommentsSortingFieldsEnum
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.domain.post_comments.services import IPostCommentService
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetPostCommentRepliesUseCase:
    post_comment_service: IPostCommentService
    post_comment_reader: IPostCommentReader
    transaction_manager: ITransactionManager

    async def execute(self, query: GetPostCommentRepliesQuery) -> tuple[list[DetailedPostCommentDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)

                cursor_id_value = UUID(decoded_cursor['id'])

                match query.sorting.sort_by:
                    case PostCommentsSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(decoded_cursor['created_at'])

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        async with self.transaction_manager:
            post_comment = await self.post_comment_service.try_get_by_id(id=query.post_comment_id)
            replies = await self.post_comment_reader.get_replies(
                post_comment_id=post_comment.id,
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
                case PostCommentsSortingFieldsEnum.CREATED_AT:
                    next_cursor['created_at'] = last_item.created_at.isoformat()

        return replies, base64url_encode(value=next_cursor) if next_cursor else None
