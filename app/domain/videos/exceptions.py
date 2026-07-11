from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class VideoNotFoundByUploadIdAndS3KeyError(AppException):
    message = 'Video not found by upload_id and s3_key'
    upload_id: str
    s3_key: str


@dataclass(kw_only=True)
class VideoNotFoundByIdError(AppException):
    message = 'Video not found by id'
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
class VideoInvalidKeyError(AppException):
    message = 'Video invalid key'
    key: str


@dataclass(kw_only=True)
class VideoAccessForbiddenError(AppException):
    message = 'Video access forbidden'
    video_id: str
    channel_id: UUID
