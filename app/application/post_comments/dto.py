from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO


@dataclass(kw_only=True, frozen=True)
class DetailedPostComment(DTO):
    id: UUID
    text: str
    reply_level: int
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime
    author_slug: str
