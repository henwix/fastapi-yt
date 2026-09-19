from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class PostCommentReactionNotFoundError(AppError):
    message = 'Post comment reaction not found'
    post_comment_id: UUID
    channel_id: UUID
