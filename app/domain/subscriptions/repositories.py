from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.domain.subscriptions.entities import Subscription


class ISubscriptionRepository(ABC):
    @abstractmethod
    async def create(self, subscription: Subscription) -> Subscription: ...

    @abstractmethod
    async def check_subscription_exists(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool: ...

    @abstractmethod
    async def delete_by_ids(self, subscriber_id: UUID, subscribed_to_id: UUID) -> bool: ...

    @abstractmethod
    async def get_many_by_subscribed_to_id(
        self,
        subscribed_to_id: UUID,
        cursor_sort_value: str | datetime | None,
        cursor_sort_id: UUID | None,
        sort_by: str,
        order: str,
        per_page: int,
    ) -> list[Subscription]: ...
