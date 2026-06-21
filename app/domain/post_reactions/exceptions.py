from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class PostReactionNotFoundError(AppException):
    message = 'Post reaction not found'
    post_id: UUID
    channel_id: UUID


@dataclass(kw_only=True)
class PostReactionAlreadyExistsError(AppException):
    message = 'Post reaction already exists'
    post_id: UUID
    channel_id: UUID
