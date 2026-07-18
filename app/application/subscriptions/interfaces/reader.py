from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.subscriptions.dto import DetailedSubscriptionDTO
from app.application.subscriptions.queries import SubscriptionsSorting


class ISubscriptionReader(ABC):
    @abstractmethod
    async def get_subscribers_by_id(
        self,
        subscribed_to_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: SubscriptionsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedSubscriptionDTO]: ...

    @abstractmethod
    async def get_subscriptions_by_id(
        self,
        subscriber_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: SubscriptionsSorting,
        pagination: CursorPagination,
    ) -> list[DetailedSubscriptionDTO]: ...
