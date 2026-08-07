from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.application.common.dto import DTO
from app.domain.video_comments.enums import VideoCommentReplyLevelEnum


@dataclass(kw_only=True, frozen=True)
class DetailedVideoCommentDTO(DTO):
    id: UUID
    text: str
    reply_level: VideoCommentReplyLevelEnum
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime
    author_slug: str
