from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.common.entities import BaseEntity
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class Subscription(BaseEntity):
    subscriber_id: UUID
    subscribed_to_id: UUID
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(subscriber_id: UUID, subscribed_to_id: UUID) -> Subscription:
        return Subscription(
            subscriber_id=subscriber_id,
            subscribed_to_id=subscribed_to_id,
        )
