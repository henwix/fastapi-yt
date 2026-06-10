from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.subscriptions.entities import Subscription
from app.domain.subscriptions.exceptions import SubscriptionAlreadyExistsError, SubscriptionNotFoundError
from app.domain.subscriptions.repositories import ISubscriptionRepository


class ISubscriptionService(ABC):
    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription: ...

    @abstractmethod
    async def check_subscription_exists(self, subscriber_id: UUID, subscribed_to_id: UUID) -> None: ...

    @abstractmethod
    async def try_delete_by_ids(self, subscriber_id: UUID, subscribed_to_id: UUID) -> None: ...


@dataclass
class SubscriptionService(ISubscriptionService):
    _subscription_repo: ISubscriptionRepository

    async def create(self, subscription: Subscription) -> Subscription:
        return await self._subscription_repo.create(subscription=subscription)

    async def check_subscription_exists(self, subscriber_id: UUID, subscribed_to_id: UUID) -> None:
        if await self._subscription_repo.check_subscription_exists(
            subscriber_id=subscriber_id,
            subscribed_to_id=subscribed_to_id,
        ):
            raise SubscriptionAlreadyExistsError(subscriber_id=subscriber_id, subscribed_to_id=subscribed_to_id)

    async def try_delete_by_ids(self, subscriber_id: UUID, subscribed_to_id: UUID) -> None:
        is_deleted = await self._subscription_repo.delete_by_ids(
            subscriber_id=subscriber_id,
            subscribed_to_id=subscribed_to_id,
        )
        if not is_deleted:
            raise SubscriptionNotFoundError(subscriber_id=subscriber_id, subscribed_to_id=subscribed_to_id)
