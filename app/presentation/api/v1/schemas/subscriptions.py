from datetime import datetime
from uuid import UUID

from app.domain.subscriptions.entities import Subscription
from app.presentation.api.v1.schemas.base import BaseSchema


class SubscriptionSchema(BaseSchema):
    subscriber_id: UUID
    subscribed_to_id: UUID
    created_at: datetime

    @staticmethod
    def from_entity(entity: Subscription) -> SubscriptionSchema:
        return SubscriptionSchema(
            subscriber_id=entity.subscriber_id,
            subscribed_to_id=entity.subscribed_to_id,
            created_at=entity.created_at,
        )
