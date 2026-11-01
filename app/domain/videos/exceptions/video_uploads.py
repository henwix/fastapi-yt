from dataclasses import dataclass

from app.domain.common.exceptions.base import AppError


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
class VideoUploadFailedToCreateError(AppError):
    message = 'Failed to create video upload'
    video_id: str
    key: str
    bucket: str


@dataclass(kw_only=True)
class VideoUploadFailedToAbortError(AppError):
    message = 'Failed to abort video upload'
    video_id: str
    key: str
    bucket: str
    exc_detail: str


@dataclass(kw_only=True)
class VideoUploadFailedToCompleteError(AppError):
    message = 'Failed to complete video upload'
    video_id: str
    key: str
    bucket: str
    exc_detail: str


@dataclass(kw_only=True)
class VideoInvalidFilenameError(AppError):
    message = 'Video invalid filename'
    filename: str


@dataclass(kw_only=True)
class VideoInvalidContentTypeError(AppError):
    message = 'Video invalid content type'
    key: str
    metadata_content_type: str
    actual_content_type: str


@dataclass(kw_only=True)
class VideoSizeTooSmallError(AppError):
    message = 'Video size too small'
    key: str
    bucket: str
    file_size: int


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
    bucket: str
    file_size: int
    file_max_size: int


@dataclass(kw_only=True)
class VideoThumbnailSizeTooSmallError(AppError):
    message = 'Video thumbnail size too small'
    key: str
    bucket: str
    file_size: int


@dataclass(kw_only=True)
class VideoThumbnailInvalidKeyError(AppError):
    message = 'Video thumbnail invalid key'
    key: str
    error_detail: str


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
class VideoThumbnailUploadConfirmationFailedError(AppError):
    message = 'Video thumbnail confirmation failed'
    video_id: str
    key: str
    bucket: str
    error_detail: str
