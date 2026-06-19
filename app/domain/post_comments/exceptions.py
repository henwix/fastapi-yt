from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class PostCommentNotFoundByIdError(AppException):
    message = 'Post comment not found by id'
    id: UUID


@dataclass(kw_only=True)
class PostCommentInvalidReplyLevel(AppException):
    message = 'Invalid reply level'
    reply_level: int
