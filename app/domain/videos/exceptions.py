from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoNotFoundError(AppException):
    message = 'Video not found'
    video_id: str


@dataclass(kw_only=True)
class VideoUploadAlreadyCompletedError(AppException):
    message = 'Video upload already completed'
    video_id: str


@dataclass(kw_only=True)
class VideoInvalidFileFormatError(AppException):
    message = 'Video invalid file format'
    file: str


@dataclass(kw_only=True)
class VideoAccessForbiddenError(AppException):
    message = 'Video access forbidden'
    video_id: str
    channel_id: UUID | None = None
