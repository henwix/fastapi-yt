from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.interfaces.transaction_manager import ITransactionManager
from app.application.posts.dto import DetailedPostDTO
from app.application.posts.interfaces.reader import IPostReader
from app.application.posts.queries import GetPostsQuery, PostsSortingFieldsEnum
from app.domain.channels.services import IChannelService
from app.domain.common.constants import Empty
from app.domain.common.exceptions import InvalidCursorError
from app.utils.base64url import base64url_decode, base64url_encode


@dataclass
class GetPostsUseCase:
    _channel_service: IChannelService
    _post_reader: IPostReader
    _transaction_manager: ITransactionManager

    async def execute(self, query: GetPostsQuery) -> tuple[list[DetailedPostDTO], str | None]:
        cursor_sort_value = None
        cursor_id_value = None

        if query.pagination.cursor is not Empty.UNSET:
            try:
                decoded_cursor = base64url_decode(value=query.pagination.cursor)

                cursor_id_value = UUID(decoded_cursor['id'])

                match query.sorting.sort_by:
                    case PostsSortingFieldsEnum.CREATED_AT:
                        cursor_sort_value = datetime.fromisoformat(
                            decoded_cursor[PostsSortingFieldsEnum.CREATED_AT.value]
                        )

            except Exception as e:
                raise InvalidCursorError(cursor=query.pagination.cursor, exc_details=str(e)) from e

        async with self._transaction_manager:
            channel = await self._channel_service.try_get_by_slug(slug=query.channel_slug)
            posts = await self._post_reader.get_many(
                channel_id=channel.id,
                cursor_sort_value=cursor_sort_value,
                cursor_id_value=cursor_id_value,
                sorting=query.sorting,
                pagination=query.pagination,
            )

        next_cursor = None

        if len(posts) > query.pagination.per_page:
            posts = posts[: query.pagination.per_page]
            last_item = posts[-1]
            next_cursor = {'id': str(last_item.id)}

            match query.sorting.sort_by:
                case PostsSortingFieldsEnum.CREATED_AT:
                    next_cursor[PostsSortingFieldsEnum.CREATED_AT.value] = last_item.created_at.isoformat()

        return posts, base64url_encode(value=next_cursor) if next_cursor else None
