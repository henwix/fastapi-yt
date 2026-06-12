from dataclasses import dataclass
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.common.sorting import SortOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetSubscribersSortOrder:
    order: SortOrderEnum


@dataclass(kw_only=True, frozen=True)
class GetSubscribersQuery:
    current_channel_id: UUID
    sorting: GetSubscribersSortOrder
    pagination: CursorPagination
