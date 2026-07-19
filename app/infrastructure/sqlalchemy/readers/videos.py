from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.videos.dto import DetailedVideoDTO, PersonalVideoDTO
from app.application.videos.interfaces.reader import IVideoReader
from app.application.videos.queries import GetPersonalVideosFilters, GetPersonalVideosSorting
from app.domain.common.constants import Empty
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoNotFoundError
from app.infrastructure.sqlalchemy.converters.videos import (
    convert_video_row_to_detailed_dto,
    convert_video_row_to_personal_video_dto,
)
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.videos import VideoORM


@dataclass
class SAVideoReader(IVideoReader):
    _session: AsyncSession

    async def try_get_detailed_by_id(self, id: str) -> DetailedVideoDTO:
        stmt = (
            select(
                VideoORM.id,
                VideoORM.title,
                VideoORM.description,
                VideoORM.privacy_status,
                VideoORM.is_reported,
                VideoORM.created_at,
                VideoORM.channel_id,
                ChannelORM.name.label('channel_name'),
                ChannelORM.slug.label('channel_slug'),
            )
            .join(ChannelORM, VideoORM.channel_id == ChannelORM.id)
            .where(VideoORM.id == id, VideoORM.upload_status == VideoUploadStatusEnum.COMPLETED.value)
        )
        result = await self._session.execute(statement=stmt)
        video_row = result.mappings().one_or_none()

        if video_row is None:
            raise VideoNotFoundError(video_id=id)

        return convert_video_row_to_detailed_dto(row=video_row)

    async def get_personal_videos(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: str | None,
        filters: GetPersonalVideosFilters,
        sorting: GetPersonalVideosSorting,
        pagination: CursorPagination,
    ) -> list[PersonalVideoDTO]:
        stmt = select(
            VideoORM.id,
            VideoORM.title,
            VideoORM.privacy_status,
            VideoORM.upload_status,
            VideoORM.created_at,
        ).where(VideoORM.channel_id == channel_id)

        sort_field = getattr(VideoORM, sorting.sort_by.value)

        if cursor_sort_value and cursor_id_value:
            cursor_tuple = tuple_(sort_field, VideoORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        if filters.privacy_status is not Empty.UNSET:
            stmt = stmt.where(VideoORM.privacy_status == filters.privacy_status.value)
        if filters.upload_status is not Empty.UNSET:
            stmt = stmt.where(VideoORM.upload_status == filters.upload_status.value)

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            VideoORM.id.desc() if sorting.order is SortingOrderEnum.DESC else VideoORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        video_rows = result.mappings().all()
        return [convert_video_row_to_personal_video_dto(row=row) for row in video_rows]
