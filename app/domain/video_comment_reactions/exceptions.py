from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoCommentReactionNotFoundError(AppException):
    message = 'Video comment reaction not found'
    video_comment_id: UUID
    channel_id: UUID


@dataclass(kw_only=True)
class VideoCommentReactionAlreadyExistsError(AppException):
    message = 'Video comment reaction already exists'
    video_comment_id: UUID
    channel_id: UUID
