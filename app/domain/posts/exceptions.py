from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppException


@dataclass(kw_only=True)
class PostNotFoundError(AppException):
    message = 'Post not found'
    id: UUID


@dataclass(kw_only=True)
class PostAccessForbiddenError(AppException):
    message = 'Post access forbidden'
    post_id: UUID
    channel_id: UUID
