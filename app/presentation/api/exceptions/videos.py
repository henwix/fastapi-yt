from fastapi import status

from app.domain.common.exceptions.base import AppError
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoCommentAccessForbiddenError,
    VideoCommentNotFoundError,
    VideoCommentReactionNotFoundError,
    VideoHistoryEmptyError,
    VideoInvalidFileContentTypeError,
    VideoInvalidFilenameError,
    VideoNotFoundError,
    VideoNotFoundInHistoryError,
    VideoReactionNotFoundError,
    VideoThumbnailAlreadySetError,
    VideoThumbnailInvalidContentTypeError,
    VideoThumbnailInvalidFilenameError,
    VideoThumbnailInvalidKeyError,
    VideoThumbnailNotFoundError,
    VideoThumbnailSizeTooBigError,
    VideoThumbnailVideoIdMismatchError,
    VideoUploadAlreadyCompletedError,
    VideoUploadAlreadyCreatedError,
    VideoUploadNotCreatedError,
    VideoViewsLimitReachedError,
)


def init_videos() -> dict[type[AppError], int]:
    return {
        # Videos
        VideoThumbnailInvalidKeyError: status.HTTP_400_BAD_REQUEST,
        VideoThumbnailInvalidFilenameError: status.HTTP_400_BAD_REQUEST,
        VideoThumbnailAlreadySetError: status.HTTP_409_CONFLICT,
        VideoThumbnailVideoIdMismatchError: status.HTTP_409_CONFLICT,
        VideoThumbnailInvalidContentTypeError: status.HTTP_409_CONFLICT,
        VideoThumbnailNotFoundError: status.HTTP_404_NOT_FOUND,
        VideoThumbnailSizeTooBigError: status.HTTP_409_CONFLICT,
        VideoUploadAlreadyCompletedError: status.HTTP_409_CONFLICT,
        VideoUploadAlreadyCreatedError: status.HTTP_409_CONFLICT,
        VideoUploadNotCreatedError: status.HTTP_409_CONFLICT,
        VideoInvalidFilenameError: status.HTTP_400_BAD_REQUEST,
        VideoInvalidFileContentTypeError: status.HTTP_409_CONFLICT,
        VideoAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        VideoNotFoundError: status.HTTP_404_NOT_FOUND,
        # Video views
        VideoViewsLimitReachedError: status.HTTP_409_CONFLICT,
        # Video reactions
        VideoReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Video comments
        VideoCommentAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        VideoCommentNotFoundError: status.HTTP_404_NOT_FOUND,
        # Video comment reactions
        VideoCommentReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Video history
        VideoNotFoundInHistoryError: status.HTTP_404_NOT_FOUND,
        VideoHistoryEmptyError: status.HTTP_404_NOT_FOUND,
    }
