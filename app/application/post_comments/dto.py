from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO
from app.domain.post_comments.enums import PostCommentReplyLevelEnum


@dataclass(kw_only=True, frozen=True)
class DetailedPostCommentDTO(DTO):
    id: UUID
    text: str
    reply_level: PostCommentReplyLevelEnum
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime
    author_slug: str
