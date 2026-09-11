from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto.base import DTO


@dataclass(kw_only=True, frozen=True)
class DetailedSubscription(DTO):
    subscription_id: UUID
    channel_slug: str
    created_at: datetime
