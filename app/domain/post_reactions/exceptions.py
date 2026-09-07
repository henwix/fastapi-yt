from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppException


@dataclass(kw_only=True)
class PostReactionNotFoundError(AppException):
    message = 'Post reaction not found'
    post_id: UUID
    channel_id: UUID
