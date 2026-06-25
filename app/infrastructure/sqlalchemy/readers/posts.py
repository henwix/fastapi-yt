from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.posts.dto import DetailedPostDTO
from app.application.posts.interfaces.reader import IPostReader
from app.application.posts.queries import PostsSorting
from app.infrastructure.sqlalchemy.models.channels import ChannelORM
from app.infrastructure.sqlalchemy.models.posts import PostORM


@dataclass
class SAPostReader(IPostReader):
    _session: AsyncSession

    async def get_many(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPostDTO]:
        stmt = (
            select(
                PostORM.id,
                PostORM.text,
                PostORM.created_at,
                ChannelORM.name,
                ChannelORM.slug,
            )
            .where(PostORM.channel_id == channel_id)
            .join(ChannelORM, PostORM.channel_id == ChannelORM.id)
        )

        sort_field = getattr(PostORM, sorting.sort_by.value)

        if cursor_sort_value and cursor_id_value:
            cursor_tuple = tuple_(sort_field, PostORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            PostORM.id.desc() if sorting.order is SortingOrderEnum.DESC else PostORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)
        result = await self._session.execute(statement=stmt)

        return [
            DetailedPostDTO(
                id=id, text=text, created_at=created_at, channel_name=channel_name, channel_slug=channel_slug
            )
            for id, text, created_at, channel_name, channel_slug in result.all()
        ]
