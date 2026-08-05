from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class Subscription(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    subscriber_id: UUID
    subscribed_to_id: UUID
    created_at: datetime = field(default_factory=get_current_utc_datetime)

    @staticmethod
    def create(subscriber_id: UUID, subscribed_to_id: UUID) -> Subscription:
        return Subscription(
            subscriber_id=subscriber_id,
            subscribed_to_id=subscribed_to_id,
        )
