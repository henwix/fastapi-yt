from dataclasses import dataclass
from datetime import datetime
from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, exists, select
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.common.sorting import SortOrderEnum
from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.exceptions import SubscriptionAlreadyExistsError
from app.domain.subscriptions.repositories import ISubscriptionRepository
from app.infrastructure.sqlalchemy.models.channels import SubscriptionORM


@dataclass
class SASubscriptionRepository(ISubscriptionRepository):
    _session: AsyncSession

    def _parse_db_error(self, error: DBAPIError, subscription: Subscription) -> NoReturn:
        cause = error.orig.__cause__
        if cause is None:
            raise

        match cause.constraint_name:
            case 'unique_channel_subscription':
                raise SubscriptionAlreadyExistsError(
                    subscriber_id=subscription.subscriber_id,
                    subscribed_to_id=subscription.subscribed_to_id,
                ) from error
            case _:
                raise

    async def create(self, subscription: Subscription) -> Subscription:
        model = SubscriptionORM.from_entity(entity=subscription)
        self._session.add(instance=model)
        try:
            await self._session.flush((model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, subscription=subscription)
        return model.to_entity()

    async def check_subscription_exists(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool:
        stmt = select(
            exists().where(
                SubscriptionORM.subscriber_id == subscriber_id, SubscriptionORM.subscribed_to_id == subscribed_to_id
            )
        )
        result = await self._session.execute(statement=stmt)
        return result.scalar_one()

    async def delete_by_ids(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool:
        stmt = delete(SubscriptionORM).where(
            SubscriptionORM.subscriber_id == subscriber_id,
            SubscriptionORM.subscribed_to_id == subscribed_to_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0

    async def get_many_by_subscribed_to_id(
        self,
        subscribed_to_id: UUID,
        cursor_sort_value: str | datetime | None,
        cursor_sort_id: UUID | None,
        sort_by: str,
        order: str,
        per_page: int,
    ) -> list[Subscription]:
        stmt = select(SubscriptionORM).where(SubscriptionORM.subscribed_to_id == subscribed_to_id)
        sort_by_field = getattr(SubscriptionORM, sort_by)

        if cursor_sort_value and cursor_sort_id:
            if order == SortOrderEnum.DESC.value:
                stmt = stmt.where(
                    (sort_by_field < cursor_sort_value)
                    | ((sort_by_field == cursor_sort_value) & (SubscriptionORM.id < cursor_sort_id))
                )
            else:
                stmt = stmt.where(
                    (sort_by_field > cursor_sort_value)
                    | ((sort_by_field == cursor_sort_value) & (SubscriptionORM.id > cursor_sort_id))
                )

        stmt = stmt.order_by(
            sort_by_field.desc() if order == SortOrderEnum.DESC.value else sort_by_field,
            SubscriptionORM.id.desc() if order == SortOrderEnum.DESC.value else SubscriptionORM.id,
        )
        stmt = stmt.limit(limit=per_page + 1)

        result = await self._session.execute(statement=stmt)
        return [sub.to_entity() for sub in result.scalars()]
