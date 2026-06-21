from datetime import datetime
from uuid import UUID

from app.application.common.sorting import SortOrderEnum
from app.application.subscriptions.dto import DetailedSubscriptionDTO
from app.application.subscriptions.queries import SubscriptionsSortFieldsEnum
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


class DetailedSubscriptionSchema(BaseSchema):
    subscription_id: UUID
    channel_slug: str
    created_at: datetime

    @staticmethod
    def from_dto(dto: DetailedSubscriptionDTO) -> DetailedSubscriptionSchema:
        return DetailedSubscriptionSchema(
            subscription_id=dto.subscription_id,
            channel_slug=dto.channel_slug,
            created_at=dto.created_at,
        )


class SubscriptionsSortParams(BaseSchema):
    sort_by: SubscriptionsSortFieldsEnum = SubscriptionsSortFieldsEnum.CREATED_AT
    order: SortOrderEnum = SortOrderEnum.DESC


class SubscriptionsCursorResponse(BaseCursorResponse):
    results: list[DetailedSubscriptionSchema]
