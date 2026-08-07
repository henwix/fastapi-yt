from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoCommentNotFoundError(AppException):
    message = 'Video comment not found'
    id: UUID


@dataclass(kw_only=True)
class VideoCommentAccessForbiddenError(AppException):
    message = 'Video comment access forbidden'
    video_comment_id: UUID
    channel_id: UUID
