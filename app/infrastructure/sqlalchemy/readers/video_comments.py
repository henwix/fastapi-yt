from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.video_comments.dto import DetailedVideoCommentDTO
from app.application.video_comments.interfaces.reader import IVideoCommentReader
from app.application.video_comments.queries import VideoCommentsSorting
from app.domain.video_comments.enums import VideoCommentReplyLevelEnum
from app.infrastructure.sqlalchemy.converters.video_comments import convert_row_to_detailed_video_comment_dto
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import VideoCommentORM


@dataclass
class SAVideoCommentReader(IVideoCommentReader):
    _session: AsyncSession

    async def _get_many_by_filters(
        self,
        *filters,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: VideoCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedVideoCommentDTO]:
        stmt = (
            select(
                VideoCommentORM.id,
                VideoCommentORM.text,
                VideoCommentORM.reply_level,
                VideoCommentORM.is_edited,
                VideoCommentORM.reply_comment_id,
                VideoCommentORM.created_at,
                ChannelORM.slug.label('author_slug'),
            )
            .where(*filters)
            .join(ChannelORM, VideoCommentORM.channel_id == ChannelORM.id)
        )

        sort_field = getattr(VideoCommentORM, sorting.sort_by.value)

        if cursor_sort_value and cursor_id_value:
            cursor_tuple = tuple_(sort_field, VideoCommentORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            VideoCommentORM.id.desc() if sorting.order is SortingOrderEnum.DESC else VideoCommentORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        video_comment_rows = result.mappings().all()
        return [convert_row_to_detailed_video_comment_dto(row=row) for row in video_comment_rows]

    async def get_comments(
        self,
        video_id: str,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: VideoCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedVideoCommentDTO]:
        return await self._get_many_by_filters(
            VideoCommentORM.video_id == video_id,
            VideoCommentORM.reply_level == VideoCommentReplyLevelEnum.ZERO.value,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )

    async def get_replies(
        self,
        video_comment_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: VideoCommentsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedVideoCommentDTO]:
        return await self._get_many_by_filters(
            VideoCommentORM.reply_comment_id == video_comment_id,
            VideoCommentORM.reply_level == VideoCommentReplyLevelEnum.ONE.value,
            cursor_sort_value=cursor_sort_value,
            cursor_id_value=cursor_id_value,
            sorting=sorting,
            pagination=pagination,
        )
