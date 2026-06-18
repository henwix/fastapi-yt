from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortOrderEnum


class SubscriptionsSortFieldsEnum(StrEnum):
    created_at = 'created_at'


@dataclass(kw_only=True, frozen=True)
class SubscriptionsSorting:
    sort_by: SubscriptionsSortFieldsEnum
    order: SortOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetSubscribersQuery:
    current_channel_id: UUID
    sorting: SubscriptionsSorting
    pagination: CursorPagination


@dataclass(kw_only=True, frozen=True)
class GetSubscriptionsQuery:
    current_channel_id: UUID
    sorting: SubscriptionsSorting
    pagination: CursorPagination
