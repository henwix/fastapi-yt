from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO


@dataclass(kw_only=True)
class ChannelAboutInfo(DTO):
    id: UUID
    name: str
    slug: str
    description: str
    country: str
    created_at: datetime
    subscribers_count: int
    videos_count: int
    views_count: int
