from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class PostReactionNotFound(AppException):
    message = 'Post reaction not found'
    post_id: UUID
    channel_id: UUID


@dataclass(kw_only=True)
class PostReactionAlreadyExists(AppException):
    message = 'Post reaction already exists'
    post_id: UUID
    channel_id: UUID
