from dataclasses import asdict
from logging import getLogger

from fastapi import Request, status

from app.domain.auth.exceptions import (
    IncorrectEmailOrPasswordError,
    JWTExpiredTokenError,
    JWTInvalidTokenError,
    NotAuthenticatedError,
)
from app.domain.channels.exceptions import (
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidFileContentTypeError,
    ChannelAvatarInvalidFileFormatError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarNotFoundError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
    ChannelWithEmailAlreadyExistsError,
    ChannelWithSlugAlreadyExistsError,
)
from app.domain.common.exceptions import (
    AppException,
    InvalidCursorError,
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3ObjectAccessForbiddenError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3UnavailableError,
)
from app.domain.post_comment_reactions.exceptions import (
    PostCommentReactionAlreadyExistsError,
    PostCommentReactionNotFoundError,
)
from app.domain.post_comments.exceptions import (
    PostCommentAccessForbiddenError,
    PostCommentInvalidReplyLevelError,
    PostCommentNotFoundByIdError,
)
from app.domain.post_reactions.exceptions import PostReactionAlreadyExistsError, PostReactionNotFoundError
from app.domain.posts.exceptions import PostAccessForbiddenError, PostNotFoundByIdError
from app.domain.subscriptions.exceptions import (
    SelfSubscriptionError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from app.domain.video_reactions.exceptions import VideoReactionAlreadyExistsError, VideoReactionNotFoundError
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileFormatError,
    VideoNotFoundByIdError,
    VideoUploadAlreadyCompletedError,
)
from app.presentation.api.responses.msgspec import MsgSpecJSONResponse

logger = getLogger(__name__)


def get_http_status_code(exc: AppException):
    exception_codes: dict[type[AppException], int] = {
        # Common
        InvalidCursorError: status.HTTP_400_BAD_REQUEST,
        S3ObjectAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        S3ObjectNotFoundError: status.HTTP_404_NOT_FOUND,
        S3MultipartUploadNotFoundError: status.HTTP_404_NOT_FOUND,
        S3MultipartUploadInvalidPartsError: status.HTTP_400_BAD_REQUEST,
        S3RequestError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        S3UnavailableError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        # Channels
        ChannelWithEmailAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        ChannelWithSlugAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidFileFormatError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidKeyError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidFileContentTypeError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarAlreadySetError: status.HTTP_400_BAD_REQUEST,
        ChannelNotFoundByIdError: status.HTTP_404_NOT_FOUND,
        ChannelNotFoundBySlugError: status.HTTP_404_NOT_FOUND,
        ChannelAvatarNotFoundError: status.HTTP_404_NOT_FOUND,
        ChannelNotActiveError: status.HTTP_403_FORBIDDEN,
        # Auth
        IncorrectEmailOrPasswordError: status.HTTP_401_UNAUTHORIZED,
        JWTInvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        JWTExpiredTokenError: status.HTTP_401_UNAUTHORIZED,
        NotAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
        # Videos
        VideoInvalidFileFormatError: status.HTTP_400_BAD_REQUEST,
        VideoUploadAlreadyCompletedError: status.HTTP_400_BAD_REQUEST,
        VideoAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        VideoNotFoundByIdError: status.HTTP_404_NOT_FOUND,
        # Video reactions
        VideoReactionAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        VideoReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Posts
        PostAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostNotFoundByIdError: status.HTTP_404_NOT_FOUND,
        # Post reactions
        PostReactionAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        PostReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post comment
        PostCommentAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostCommentNotFoundByIdError: status.HTTP_404_NOT_FOUND,
        PostCommentInvalidReplyLevelError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        # Post comment reactions
        PostCommentReactionAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        PostCommentReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Subscriptions
        SubscriptionAlreadyExistsError: status.HTTP_400_BAD_REQUEST,
        SelfSubscriptionError: status.HTTP_400_BAD_REQUEST,
        SubscriptionNotFoundError: status.HTTP_404_NOT_FOUND,
    }
    return exception_codes.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


async def exception_handler(
    _: Request,
    exc: AppException,
) -> MsgSpecJSONResponse:
    logger.error(msg=exc.message, extra={'log_meta': asdict(exc)})
    return MsgSpecJSONResponse(
        content={'detail': exc.message},
        status_code=get_http_status_code(exc=exc),
    )
