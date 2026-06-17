from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortOrderEnum


class GetSubscribersSortFieldsEnum(StrEnum):
    created_at = 'created_at'


@dataclass(kw_only=True, frozen=True)
class GetSubscribersSortOrder:
    sort_by: GetSubscribersSortFieldsEnum
    order: SortOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetSubscribersQuery:
    current_channel_id: UUID
    sorting: GetSubscribersSortOrder
    pagination: CursorPagination


class GetSubscriptionsSortFieldsEnum(StrEnum):
    created_at = 'created_at'


@dataclass(kw_only=True, frozen=True)
class GetSubscriptionsSortOrder:
    sort_by: GetSubscriptionsSortFieldsEnum
    order: SortOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetSubscriptionsQuery:
    current_channel_id: UUID
    sorting: GetSubscriptionsSortOrder
    pagination: CursorPagination
