from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, tuple_
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortOrderEnum
from app.application.subscriptions.dto import DetailedSubscriberDTO, DetailedSubscriptionDTO
from app.application.subscriptions.interfaces.reader import ISubscriptionReader
from app.application.subscriptions.queries import GetSubscribersSortOrder, GetSubscriptionsSortOrder
from app.infrastructure.sqlalchemy.models.channels import ChannelORM, SubscriptionORM


@dataclass
class SASubscriptionReader(ISubscriptionReader):
    _session: AsyncSession

    async def get_subscribers_by_id(
        self,
        subscribed_to_id: UUID,
        cursor_sort_value: str | datetime | None,
        cursor_sort_id: UUID | None,
        sorting: GetSubscribersSortOrder,
        pagination: CursorPagination,
    ) -> list[DetailedSubscriberDTO]:
        stmt = (
            select(SubscriptionORM.id, SubscriptionORM.created_at, ChannelORM.slug)
            .where(SubscriptionORM.subscribed_to_id == subscribed_to_id)
            .join(ChannelORM, SubscriptionORM.subscriber_id == ChannelORM.id)
        )
        sort_by_field = getattr(SubscriptionORM, sorting.sort_by.value)

        if cursor_sort_value and cursor_sort_id:
            cursor_tuple = tuple_(sort_by_field, SubscriptionORM.id)

            if sorting.order is SortOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_sort_id))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_sort_id))
        stmt = stmt.order_by(
            sort_by_field.desc() if sorting.order is SortOrderEnum.DESC else sort_by_field,
            SubscriptionORM.id.desc() if sorting.order == SortOrderEnum.DESC else SubscriptionORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        return [
            DetailedSubscriberDTO(subscription_id=id, created_at=created_at, channel_slug=slug)
            for id, created_at, slug in result.all()
        ]

    async def get_subscriptions_by_id(
        self,
        subscriber_id: UUID,
        cursor_sort_value: str | datetime | None,
        cursor_sort_id: UUID,
        sorting: GetSubscriptionsSortOrder,
        pagination: CursorPagination,
    ) -> list[DetailedSubscriptionDTO]:
        stmt = (
            select(SubscriptionORM.id, SubscriptionORM.created_at, ChannelORM.slug)
            .where(SubscriptionORM.subscriber_id == subscriber_id)
            .join(ChannelORM, SubscriptionORM.subscribed_to_id == ChannelORM.id)
        )

        sort_by_field = getattr(SubscriptionORM, sorting.sort_by.value)
        if cursor_sort_value and cursor_sort_id:
            cursor_tuple = tuple_(sort_by_field, SubscriptionORM.id)

            if sorting.order is SortOrderEnum.DESC:
                stmt = stmt.where(cursor_tuple < (cursor_sort_value, cursor_sort_id))
            else:
                stmt = stmt.where(cursor_tuple > (cursor_sort_value, cursor_sort_id))

        stmt = stmt.order_by(
            sort_by_field.desc() if sorting.order is SortOrderEnum.DESC else sort_by_field,
            SubscriptionORM.id.desc() if sorting.order is SortOrderEnum.DESC else SubscriptionORM.id,
        )
        stmt = stmt.limit(limit=pagination.per_page + 1)

        result = await self._session.execute(statement=stmt)
        return [
            DetailedSubscriptionDTO(subscription_id=id, channel_slug=slug, created_at=created_at)
            for id, created_at, slug in result.all()
        ]
