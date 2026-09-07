from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppException


@dataclass(kw_only=True)
class VideoCommentReactionNotFoundError(AppException):
    message = 'Video comment reaction not found'
    video_comment_id: UUID
    channel_id: UUID
