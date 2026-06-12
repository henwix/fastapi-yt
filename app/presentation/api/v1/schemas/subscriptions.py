from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from app.application.common.sorting import SortOrderEnum
from app.domain.subscriptions.entities import Subscription
from app.presentation.api.v1.schemas.base import BaseSchema


class SubscriptionSchema(BaseSchema):
    id: UUID
    subscriber_id: UUID
    subscribed_to_id: UUID
    created_at: datetime

    @staticmethod
    def from_entity(entity: Subscription) -> SubscriptionSchema:
        return SubscriptionSchema(
            id=entity.id,
            subscriber_id=entity.subscriber_id,
            subscribed_to_id=entity.subscribed_to_id,
            created_at=entity.created_at,
        )


class SubscriptionSortParams(BaseSchema):
    order: SortOrderEnum = SortOrderEnum.DESC


class SubscriptionCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[SubscriptionSchema]
