from typing import NoReturn, cast
from uuid import UUID

from sqlalchemy import CursorResult, delete, exists, select
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.exceptions import SelfSubscriptionError, SubscriptionAlreadyExistsError
from app.domain.subscriptions.repos import ISubscriptionRepo
from app.infrastructure.sqlalchemy.models import SubscriptionORM
from app.infrastructure.sqlalchemy.repos.base import SQLAlchemyRepo


class SubscriptionRepo(SQLAlchemyRepo, ISubscriptionRepo):
    def _parse_db_error(self, error: DBAPIError, subscription: Subscription) -> NoReturn:
        constraint_name = self._extract_constraint_name(error=error)

        match constraint_name:
            case 'unique_channel_subscription':
                raise SubscriptionAlreadyExistsError(
                    subscriber_id=subscription.subscriber_id,
                    subscribed_to_id=subscription.subscribed_to_id,
                ) from error

            case 'ck_no_self_subscriptions':
                raise SelfSubscriptionError(subscriber_id=subscription.subscriber_id) from error
            case 'subscriptions_subscribed_to_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=subscription.subscribed_to_id) from error
            case 'subscriptions_subscriber_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=subscription.subscriber_id) from error
            case _:
                raise

    async def create(self, subscription: Subscription) -> Subscription:
        model = SubscriptionORM.from_entity(entity=subscription)
        async with self._db.get_session(commit=True) as session:
            session.add(instance=model)
            try:
                await session.flush(objects=(model,))
            except IntegrityError as e:
                self._parse_db_error(error=e, subscription=subscription)
        return model.to_entity()

    async def check_subscription_exists(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool:
        stmt = select(
            exists().where(
                SubscriptionORM.subscriber_id == subscriber_id, SubscriptionORM.subscribed_to_id == subscribed_to_id
            )
        )
        async with self._db.get_session(commit=False) as session:
            result = await session.execute(statement=stmt)
        return result.scalar_one()

    async def delete_by_ids(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool:
        stmt = delete(SubscriptionORM).where(
            SubscriptionORM.subscriber_id == subscriber_id,
            SubscriptionORM.subscribed_to_id == subscribed_to_id,
        )
        async with self._db.get_session(commit=True) as session:
            result = await session.execute(statement=stmt)
        return cast(CursorResult, result).rowcount > 0
