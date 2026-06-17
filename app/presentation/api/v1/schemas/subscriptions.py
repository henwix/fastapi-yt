from datetime import datetime
from uuid import UUID

from app.application.common.sorting import SortOrderEnum
from app.application.subscriptions.dto import DetailedSubscriberDTO, DetailedSubscriptionDTO
from app.application.subscriptions.queries import GetSubscribersSortFieldsEnum, GetSubscriptionsSortFieldsEnum
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


class DetailedSubscriberSchema(BaseSchema):
    subscription_id: UUID
    channel_slug: str
    created_at: datetime

    @staticmethod
    def from_dto(dto: DetailedSubscriberDTO) -> DetailedSubscriberSchema:
        return DetailedSubscriberSchema(
            subscription_id=dto.subscription_id,
            channel_slug=dto.channel_slug,
            created_at=dto.created_at,
        )


class GetSubscribersSortParams(BaseSchema):
    sort_by: GetSubscribersSortFieldsEnum = GetSubscribersSortFieldsEnum.created_at
    order: SortOrderEnum = SortOrderEnum.DESC


class GetSubscribersCursorResponse(BaseCursorResponse):
    results: list[DetailedSubscriberSchema]


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


class GetSubscriptionsSortParams(BaseSchema):
    sort_by: GetSubscriptionsSortFieldsEnum = GetSubscriptionsSortFieldsEnum.created_at
    order: SortOrderEnum = SortOrderEnum.DESC


class GetSubscriptionsCursorResponse(BaseCursorResponse):
    results: list[DetailedSubscriptionSchema]
