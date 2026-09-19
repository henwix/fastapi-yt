from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class VideoCommentNotFoundError(AppError):
    message = 'Video comment not found'
    id: UUID


@dataclass(kw_only=True)
class VideoCommentAccessForbiddenError(AppError):
    message = 'Video comment access forbidden'
    video_comment_id: UUID
    channel_id: UUID
