from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class PostNotFoundError(AppError):
    message = 'Post not found'
    id: UUID


@dataclass(kw_only=True)
class PostAccessForbiddenError(AppError):
    message = 'Post access forbidden'
    post_id: UUID
    channel_id: UUID
