from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.post_comments.dto import DetailedPostCommentDTO
from app.application.post_comments.interfaces.reader import IPostCommentReader
from app.application.post_comments.queries import PostCommentsSorting
from app.infrastructure.sqlalchemy.converters.post_comments import convert_row_to_detailed_post_comment_dto
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.posts import PostCommentORM
from app.infrastructure.sqlalchemy.readers.base import SAReader


class SAPostCommentReader(SAReader, IPostCommentReader):
    async def _get_many_by_filters(
        self,
        *filters,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostCommentDTO]:
        stmt = (
            select(
                PostCommentORM.id,
                PostCommentORM.text,
                PostCommentORM.reply_level,
                PostCommentORM.is_edited,
                PostCommentORM.reply_comment_id,
                PostCommentORM.created_at,
                ChannelORM.slug.label('author_slug'),
            )
            .where(*filters)
            .join(ChannelORM, PostCommentORM.channel_id == ChannelORM.id)
        )

        sort_field = getattr(PostCommentORM, sorting.sort_by.value)

        if cursor_sort_value is not None and cursor_id_value is not None:
            cursor_tuple = tuple_(sort_field, PostCommentORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            PostCommentORM.id.desc() if sorting.order is SortingOrderEnum.DESC else PostCommentORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        post_comment_rows = result.mappings().all()
        return [convert_row_to_detailed_post_comment_dto(row=row) for row in post_comment_rows]

    async def get_comments(
        self,
        post_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostCommentDTO]:
        return await self._get_many_by_filters(
            PostCommentORM.post_id == post_id,
            PostCommentORM.reply_level == 0,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )

    async def get_replies(
        self,
        post_comment_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostCommentDTO]:
        return await self._get_many_by_filters(
            PostCommentORM.reply_comment_id == post_comment_id,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )
