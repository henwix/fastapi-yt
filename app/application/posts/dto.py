from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO


@dataclass(kw_only=True, frozen=True)
class DetailedPostDTO(DTO):
    id: UUID
    text: str
    created_at: datetime
    channel_name: str
    channel_slug: str
