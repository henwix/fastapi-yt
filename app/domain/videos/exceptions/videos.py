from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class VideoAccessForbiddenError(AppError):
    message = 'Video access forbidden'
    video_id: str
    channel_id: UUID | None = None


@dataclass(kw_only=True)
class VideoNotFoundError(AppError):
    message = 'Video not found'
    video_id: str


@dataclass(kw_only=True)
class VideoThumbnailNotFoundError(AppError):
    message = 'Video thumbnail not found'
    video_id: str
