from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from app.application.subscriptions.dto import DetailedSubscriptionDTO
from app.domain.subscriptions.entities import Subscription
from app.presentation.api.v1.schemas.base import BaseSchema


class SubscriptionOutSchema(BaseSchema):
    id: UUID
    subscriber_id: UUID
    subscribed_to_id: UUID
    created_at: datetime

    @staticmethod
    def from_entity(entity: Subscription) -> SubscriptionOutSchema:
        return SubscriptionOutSchema(
            id=entity.id,
            subscriber_id=entity.subscriber_id,
            subscribed_to_id=entity.subscribed_to_id,
            created_at=entity.created_at,
        )


class DetailedSubscriptionOutSchema(BaseSchema):
    subscription_id: UUID
    channel_slug: str
    created_at: datetime

    @staticmethod
    def from_dto(dto: DetailedSubscriptionDTO) -> DetailedSubscriptionOutSchema:
        return DetailedSubscriptionOutSchema(
            subscription_id=dto.subscription_id,
            channel_slug=dto.channel_slug,
            created_at=dto.created_at,
        )


class SubscriptionsCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[DetailedSubscriptionOutSchema]
