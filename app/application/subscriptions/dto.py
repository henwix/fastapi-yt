from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO


@dataclass(kw_only=True, frozen=True)
class DetailedSubscriberDTO(DTO):
    subscription_id: UUID
    channel_slug: str
    created_at: datetime


@dataclass(kw_only=True, frozen=True)
class DetailedSubscriptionDTO(DTO):
    subscription_id: UUID
    channel_slug: str
    created_at: datetime
