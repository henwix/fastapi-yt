from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class VideoNotFoundError(AppError):
    message = 'Video not found'
    video_id: str


@dataclass(kw_only=True)
class VideoUploadAlreadyCompletedError(AppError):
    message = 'Video upload already completed'
    video_id: str


@dataclass(kw_only=True)
class VideoUploadAlreadyCreatedError(AppError):
    message = 'Video already has an active upload'
    video_id: str


@dataclass(kw_only=True)
class VideoUploadNotCreatedError(AppError):
    message = 'Video upload not created'
    video_id: str


@dataclass(kw_only=True)
class VideoInvalidFilenameError(AppError):
    message = 'Video invalid filename'
    filename: str


@dataclass(kw_only=True)
class VideoThumbnailAlreadySetError(AppError):
    message = 'This video thumbnail is already set'
    video_id: str
    thumbnail_s3_key: str


@dataclass(kw_only=True)
class VideoThumbnailVideoIdMismatchError(AppError):
    message = 'Thumbnail does not belong to the specified video'
    video_id: str
    metadata_video_id: str
    thumbnail_s3_key: str


@dataclass(kw_only=True)
class VideoThumbnailSizeTooBigError(AppError):
    message = 'Video thumbnail size too big'
    key: str
    file_size: int
    file_max_size: int


@dataclass(kw_only=True)
class VideoThumbnailInvalidKeyError(AppError):
    message = 'Video thumbnail invalid key'
    key: str


@dataclass(kw_only=True)
class VideoThumbnailInvalidFilenameError(AppError):
    message = 'Video thumbnail invalid filename'
    filename: str


@dataclass(kw_only=True)
class VideoThumbnailInvalidContentTypeError(AppError):
    message = 'Video thumbnail invalid content type'
    key: str
    metadata_content_type: str
    actual_content_type: str


@dataclass(kw_only=True)
class VideoThumbnailNotFoundError(AppError):
    message = 'Video thumbnail not found'
    video_id: str


@dataclass(kw_only=True)
class VideoInvalidFileContentTypeError(AppError):
    message = 'Video invalid content type'
    key: str
    metadata_content_type: str
    actual_content_type: str


@dataclass(kw_only=True)
class VideoAccessForbiddenError(AppError):
    message = 'Video access forbidden'
    video_id: str
    channel_id: UUID | None = None
