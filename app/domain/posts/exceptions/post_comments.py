from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class PostCommentNotFoundError(AppError):
    message = 'Post comment not found'
    id: UUID


@dataclass(kw_only=True)
class PostCommentAccessForbiddenError(AppError):
    message = 'Post comment access forbidden'
    post_comment_id: UUID
    channel_id: UUID
