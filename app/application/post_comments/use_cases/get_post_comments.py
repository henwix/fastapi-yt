from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.post_comments.dto import DetailedPostCommentDTO
from app.application.post_comments.interfaces.reader import IPostCommentReader
from app.application.post_comments.queries import GetPostCommentsQuery, PostCommentsSortFieldsEnum
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.domain.posts.services import IPostService
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetPostCommentsUseCase:
    post_service: IPostService
    post_comment_reader: IPostCommentReader
    transaction_manager: ITransactionManager

    async def execute(self, query: GetPostCommentsQuery) -> tuple[list[DetailedPostCommentDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)
                match query.sorting.sort_by:
                    case PostCommentsSortFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(decoded_cursor['created_at'])
                        cursor_id_value = UUID(decoded_cursor['id'])

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        async with self.transaction_manager:
            post = await self.post_service.try_get_by_id(id=query.post_id)
            comments = await self.post_comment_reader.get_many(
                post_id=post.id,
                cursor_sort_value=cursor_sort_value,
                cursor_id_value=cursor_id_value,
                sorting=query.sorting,
                pagination=query.pagination,
            )

        next_cursor = None

        if len(comments) > query.pagination.per_page:
            comments = comments[: query.pagination.per_page]
            last_item = comments[-1]

            match query.sorting.sort_by:
                case PostCommentsSortFieldsEnum.CREATED_AT:
                    next_cursor = {
                        'created_at': last_item.created_at.isoformat(),
                        'id': str(last_item.id),
                    }
        return comments, base64url_encode(value=next_cursor) if next_cursor else None
