from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.video_history.dto import PreviewVideoHistoryDTO
from app.application.video_history.interfaces.reader import IVideoHistoryReader
from app.application.video_history.queries import VideoHistorySorting, VideoHistorySortingFieldsEnum
from app.infrastructure.sqlalchemy.converters.video_history import convert_row_to_preview_video_history_dto
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import VideoHistoryItemORM, VideoORM


@dataclass
class SAVideoHistoryReader(IVideoHistoryReader):
    _session: AsyncSession

    async def get_many(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: str | None,
        sorting: VideoHistorySorting,
        pagination: CursorPagination,
    ) -> list[PreviewVideoHistoryDTO]:
        stmt = (
            select(
                VideoORM.id,
                VideoORM.title,
                VideoORM.privacy_status,
                VideoORM.created_at,
                VideoORM.views_count,
                VideoHistoryItemORM.created_at.label('watched_at'),
                ChannelORM.name.label('author_name'),
                ChannelORM.slug.label('author_slug'),
            )
            .join(VideoORM, VideoHistoryItemORM.video_id == VideoORM.id)
            .join(ChannelORM, VideoORM.channel_id == ChannelORM.id)
            .where(VideoHistoryItemORM.channel_id == channel_id)
        )

        match sorting.sort_by:
            case VideoHistorySortingFieldsEnum.WATCHED_AT:
                sort_field = VideoHistoryItemORM.created_at

        if cursor_sort_value is not None and cursor_id_value is not None:
            cursor_tuple = tuple_(sort_field, VideoHistoryItemORM.video_id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            VideoHistoryItemORM.video_id.desc()
            if sorting.order is SortingOrderEnum.DESC
            else VideoHistoryItemORM.video_id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        video_history_rows = result.mappings().all()
        return [convert_row_to_preview_video_history_dto(row=row) for row in video_history_rows]
