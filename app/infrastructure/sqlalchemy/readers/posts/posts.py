from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.posts.dto import DetailedPost
from app.application.posts.interfaces import IPostReader
from app.application.posts.queries import PostsSorting
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.posts.exceptions import PostNotFoundError
from app.infrastructure.sqlalchemy.converters.posts import convert_row_to_detailed_post_dto
from app.infrastructure.sqlalchemy.models import ChannelORM, FileORM, PostORM
from app.infrastructure.sqlalchemy.readers.base import SQLAlchemyReader


class PostReader(SQLAlchemyReader, IPostReader):
    async def get_many_by_channel_id(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PostsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedPost]:
        stmt = (
            select(
                PostORM.id,
                PostORM.text,
                PostORM.created_at,
                ChannelORM.name.label('channel_name'),
                ChannelORM.slug.label('channel_slug'),
                FileORM.key.label('channel_avatar_key'),
            )
            .join(ChannelORM, PostORM.channel_id == ChannelORM.id)
            .outerjoin(FileORM, ChannelORM.avatar_file_id == FileORM.id)
            .where(PostORM.channel_id == channel_id)
        )

        sort_field = getattr(PostORM, sorting.sort_by.value)

        if cursor_sort_value is not None and cursor_id_value is not None:
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
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)

        rows = result.mappings().all()
        return [convert_row_to_detailed_post_dto(row=row) for row in rows]

    async def try_get_detailed_by_id(self, id: UUID) -> DetailedPost:
        stmt = (
            select(
                PostORM.id,
                PostORM.text,
                PostORM.created_at,
                ChannelORM.name.label('channel_name'),
                ChannelORM.slug.label('channel_slug'),
                FileORM.key.label('channel_avatar_key'),
            )
            .join(ChannelORM, PostORM.channel_id == ChannelORM.id)
            .outerjoin(FileORM, ChannelORM.avatar_file_id == FileORM.id)
            .where(
                PostORM.id == id,
                ChannelORM.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value,
            )
        )
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)

        post = result.mappings().one_or_none()
        if post is None:
            raise PostNotFoundError(post_id=id)
        return convert_row_to_detailed_post_dto(row=post)
