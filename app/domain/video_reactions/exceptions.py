from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoReactionNotFoundError(AppException):
    message = 'Video reaction not found'
    video_id: str
    channel_id: UUID


@dataclass(kw_only=True)
class VideoReactionAlreadyExistsError(AppException):
    message = 'Video reaction already exists'
    video_id: str
    channel_id: UUID
