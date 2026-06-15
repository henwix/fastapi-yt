from datetime import datetime
from uuid import UUID

from app.application.common.sorting import SortOrderEnum
from app.application.queries.subscriptions import GetSubscribersSortFieldsEnum
from app.domain.subscriptions.entities import Subscription
from app.presentation.api.v1.schemas.base import BaseCursorResponse, BaseSchema


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
    sort_by: GetSubscribersSortFieldsEnum = GetSubscribersSortFieldsEnum.created_at
    order: SortOrderEnum = SortOrderEnum.DESC


class SubscriptionCursorResponse(BaseCursorResponse):
    results: list[SubscriptionSchema]
