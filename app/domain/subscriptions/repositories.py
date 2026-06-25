from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.subscriptions.entities import Subscription


class ISubscriptionRepository(ABC):
    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription: ...

    @abstractmethod
    async def check_subscription_exists(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool: ...

    @abstractmethod
    async def delete_by_ids(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool: ...
