from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.post_comments.dto import DetailedPostCommentDTO
from app.application.post_comments.interfaces.reader import IPostCommentReader
from app.application.post_comments.queries import PostCommentsSorting
from app.domain.post_comments.enums import PostCommentReplyLevelEnum
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.posts import PostCommentORM


@dataclass
class SAPostCommentReader(IPostCommentReader):
    _session: AsyncSession

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
                ChannelORM.slug,
            )
            .where(*filters)
            .join(ChannelORM, PostCommentORM.channel_id == ChannelORM.id)
        )

        sort_field = getattr(PostCommentORM, sorting.sort_by.value)

        if cursor_sort_value and cursor_id_value:
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

        return [
            DetailedPostCommentDTO(
                id=id,
                text=text,
                reply_level=PostCommentReplyLevelEnum.ZERO if reply_level == 0 else PostCommentReplyLevelEnum.ONE,
                is_edited=is_edited,
                reply_comment_id=reply_comment_id,
                created_at=created_at,
                author_slug=author_slug,
            )
            for id, text, reply_level, is_edited, reply_comment_id, created_at, author_slug in result.all()
        ]

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
            PostCommentORM.reply_level == PostCommentReplyLevelEnum.ZERO.value,
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
            PostCommentORM.reply_level == PostCommentReplyLevelEnum.ONE.value,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )
