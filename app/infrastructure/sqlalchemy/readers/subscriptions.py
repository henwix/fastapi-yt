from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortingOrderEnum
from app.application.subscriptions.dto import DetailedSubscription
from app.application.subscriptions.interfaces import ISubscriptionReader
from app.application.subscriptions.queries import SubscriptionsSorting
from app.infrastructure.sqlalchemy.converters.subscriptions import convert_row_to_detailed_subscription_dto
from app.infrastructure.sqlalchemy.models import ChannelORM, FileORM, SubscriptionORM
from app.infrastructure.sqlalchemy.readers.base import SQLAlchemyReader


class SubscriptionReader(SQLAlchemyReader, ISubscriptionReader):
    async def get_subscribers_by_id(
        self,
        subscribed_to_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: SubscriptionsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedSubscription]:
        stmt = (
            select(
                SubscriptionORM.id,
                SubscriptionORM.created_at,
                ChannelORM.slug,
                FileORM.key.label('avatar_key'),
            )
            .where(SubscriptionORM.subscribed_to_id == subscribed_to_id)
            .join(ChannelORM, SubscriptionORM.subscriber_id == ChannelORM.id)
            .outerjoin(FileORM, ChannelORM.avatar_file_id == FileORM.id)
        )
        sort_field = getattr(SubscriptionORM, sorting.sort_by.value)

        if cursor_sort_value is not None and cursor_id_value is not None:
            cursor_tuple = tuple_(sort_field, SubscriptionORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))
        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            SubscriptionORM.id.desc() if sorting.order == SortingOrderEnum.DESC else SubscriptionORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        rows = result.mappings().all()
        return [convert_row_to_detailed_subscription_dto(row) for row in rows]

    async def get_subscriptions_by_id(
        self,
        subscriber_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: SubscriptionsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedSubscription]:
        stmt = (
            select(
                SubscriptionORM.id,
                SubscriptionORM.created_at,
                ChannelORM.slug,
                FileORM.key.label('avatar_key'),
            )
            .where(SubscriptionORM.subscriber_id == subscriber_id)
            .join(ChannelORM, SubscriptionORM.subscribed_to_id == ChannelORM.id)
            .outerjoin(FileORM, ChannelORM.avatar_file_id == FileORM.id)
        )

        sort_field = getattr(SubscriptionORM, sorting.sort_by.value)
        if cursor_sort_value is not None and cursor_id_value is not None:
            cursor_tuple = tuple_(sort_field, SubscriptionORM.id)

            if sorting.order is SortingOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_id_value))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_id_value))

        stmt = stmt.order_by(
            sort_field.desc() if sorting.order is SortingOrderEnum.DESC else sort_field,
            SubscriptionORM.id.desc() if sorting.order is SortingOrderEnum.DESC else SubscriptionORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        rows = result.mappings().all()
        return [convert_row_to_detailed_subscription_dto(row) for row in rows]
