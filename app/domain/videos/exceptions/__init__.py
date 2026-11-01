from .video_comment_reactions import VideoCommentReactionNotFoundError
from .video_comments import VideoCommentAccessForbiddenError, VideoCommentNotFoundError
from .video_history import VideoHistoryEmptyError, VideoNotFoundInHistoryError
from .video_reactions import VideoReactionNotFoundError
from .video_uploads import (
    VideoInvalidContentTypeError,
    VideoInvalidFilenameError,
    VideoSizeTooSmallError,
    VideoThumbnailAlreadySetError,
    VideoThumbnailInvalidContentTypeError,
    VideoThumbnailInvalidFilenameError,
    VideoThumbnailInvalidKeyError,
    VideoThumbnailSizeTooBigError,
    VideoThumbnailSizeTooSmallError,
    VideoThumbnailUploadConfirmationFailedError,
    VideoThumbnailVideoIdMismatchError,
    VideoUploadAlreadyCompletedError,
    VideoUploadAlreadyCreatedError,
    VideoUploadFailedToAbortError,
    VideoUploadFailedToCompleteError,
    VideoUploadFailedToCreateError,
    VideoUploadNotCreatedError,
)
from .video_views import VideoViewsLimitReachedError
from .videos import (
    VideoAccessForbiddenError,
    VideoFileNotFoundError,
    VideoNotFoundError,
    VideoThumbnailNotFoundError,
)

__all__ = (
    'VideoAccessForbiddenError',
    'VideoCommentAccessForbiddenError',
    'VideoCommentNotFoundError',
    'VideoCommentReactionNotFoundError',
    'VideoFileNotFoundError',
    'VideoHistoryEmptyError',
    'VideoInvalidContentTypeError',
    'VideoInvalidFilenameError',
    'VideoNotFoundError',
    'VideoNotFoundInHistoryError',
    'VideoReactionNotFoundError',
    'VideoSizeTooSmallError',
    'VideoThumbnailAlreadySetError',
    'VideoThumbnailInvalidContentTypeError',
    'VideoThumbnailInvalidFilenameError',
    'VideoThumbnailInvalidKeyError',
    'VideoThumbnailNotFoundError',
    'VideoThumbnailSizeTooBigError',
    'VideoThumbnailSizeTooSmallError',
    'VideoThumbnailUploadConfirmationFailedError',
    'VideoThumbnailVideoIdMismatchError',
    'VideoUploadAlreadyCompletedError',
    'VideoUploadAlreadyCreatedError',
    'VideoUploadCreationFailedError',
    'VideoUploadFailedToAbortError',
    'VideoUploadFailedToCompleteError',
    'VideoUploadFailedToCreateError',
    'VideoUploadNotCreatedError',
    'VideoViewsLimitReachedError',
)
