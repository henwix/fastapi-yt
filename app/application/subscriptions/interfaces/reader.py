from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.subscriptions.dto import DetailedSubscriberDTO, DetailedSubscriptionDTO
from app.application.subscriptions.queries import GetSubscribersSortOrder, GetSubscriptionsSortOrder


class ISubscriptionReader(ABC):
    @abstractmethod
    async def get_subscribers_by_id(
        self,
        subscribed_to_id: UUID,
        cursor_sort_value: str | datetime | None,
        cursor_sort_id: UUID | None,
        sorting: GetSubscribersSortOrder,
        pagination: CursorPagination,
    ) -> list[DetailedSubscriberDTO]: ...

    @abstractmethod
    async def get_subscriptions_by_id(
        self,
        subscriber_id: UUID,
        cursor_sort_value: str | datetime | None,
        cursor_sort_id: UUID | None,
        sorting: GetSubscriptionsSortOrder,
        pagination: CursorPagination,
    ) -> list[DetailedSubscriptionDTO]: ...
