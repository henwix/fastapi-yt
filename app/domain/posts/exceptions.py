from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class PostNotFoundByIdError(AppException):
    message = 'Post not found by id'
    id: UUID


@dataclass(kw_only=True)
class PostAccessForbiddenError(AppException):
    message = 'Post access forbidden'
    post_id: UUID
    channel_id: UUID
