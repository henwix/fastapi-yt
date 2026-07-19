from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class PostCommentNotFoundError(AppException):
    message = 'Post comment not found'
    id: UUID


@dataclass(kw_only=True)
class PostCommentInvalidReplyLevelError(AppException):
    message = 'Invalid reply level'
    reply_level: int


@dataclass(kw_only=True)
class PostCommentAccessForbiddenError(AppException):
    message = 'Post comment access forbidden'
    post_comment_id: UUID
    channel_id: UUID
