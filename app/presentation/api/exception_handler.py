from dataclasses import asdict
from logging import getLogger

from fastapi import Request, status

from app.domain.auth.exceptions import (
    ChannelAlreadyActivatedError,
    ChannelEmailAlreadyAssociatedWithThisAcccountError,
    ChannelInvalidEmailCodeError,
    ChannelInvalidEmailUIDError,
    IncorrectEmailOrPasswordError,
    JWTTokenExpiredError,
    JWTTokenInvalidError,
    JWTTokenNotFoundError,
    NotAuthenticatedError,
)
from app.domain.channels.exceptions import (
    ChannelActivationFailedError,
    ChannelAvatarAlreadySetError,
    ChannelAvatarInvalidContentTypeError,
    ChannelAvatarInvalidFilenameError,
    ChannelAvatarInvalidKeyError,
    ChannelAvatarNotFoundError,
    ChannelAvatarSizeTooBigError,
    ChannelEmailAlreadyExistsError,
    ChannelEmailInvalidFormatError,
    ChannelEmailTooLongError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
    ChannelNotFoundBySlugError,
    ChannelSlugAlreadyExistsError,
    ChannelSlugInvalidFormatError,
)
from app.domain.common.exceptions.base import AppException
from app.domain.common.exceptions.pagination import InvalidCursorError
from app.domain.common.exceptions.s3 import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3ObjectAccessForbiddenError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3ResponseError,
)
from app.domain.oauth.exceptions import (
    OAuthAccountNotConnectedError,
    OAuthAccountUnableToDisconnectError,
    OAuthInvalidCodeError,
    OAuthInvalidStateError,
    OAuthNoAccountsConnectedError,
    OAuthProviderAlreadyConnectedError,
    OAuthProviderEmailNotVerifiedError,
    OAuthProviderReceivedInvalidResponseError,
    OAuthProviderRequestError,
    OAuthProviderResponseError,
)
from app.domain.playlists.exceptions import (
    PlaylistAccessForbiddenError,
    PlaylistNotFoundError,
    VideoAlreadyAddedToPlaylistError,
    VideoNotFoundInPlaylistError,
)
from app.domain.post_comment_reactions.exceptions import (
    PostCommentReactionNotFoundError,
)
from app.domain.post_comments.exceptions import (
    PostCommentAccessForbiddenError,
    PostCommentNotFoundError,
)
from app.domain.post_reactions.exceptions import PostReactionNotFoundError
from app.domain.posts.exceptions import PostAccessForbiddenError, PostNotFoundError
from app.domain.subscriptions.exceptions import (
    SelfSubscriptionError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from app.domain.video_comment_reactions.exceptions import (
    VideoCommentReactionNotFoundError,
)
from app.domain.video_comments.exceptions import VideoCommentAccessForbiddenError, VideoCommentNotFoundError
from app.domain.video_history.exceptions import VideoHistoryEmptyError, VideoNotFoundInHistoryError
from app.domain.video_reactions.exceptions import VideoReactionNotFoundError
from app.domain.video_views.exceptions import VideoViewsLimitReachedError
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileContentTypeError,
    VideoInvalidFilenameError,
    VideoNotFoundError,
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
        S3ResponseError: status.HTTP_502_BAD_GATEWAY,
        # Channels
        ChannelEmailAlreadyExistsError: status.HTTP_409_CONFLICT,
        ChannelEmailInvalidFormatError: status.HTTP_400_BAD_REQUEST,
        ChannelEmailTooLongError: status.HTTP_400_BAD_REQUEST,
        ChannelSlugAlreadyExistsError: status.HTTP_409_CONFLICT,
        ChannelSlugInvalidFormatError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidKeyError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidFilenameError: status.HTTP_400_BAD_REQUEST,
        ChannelAvatarInvalidContentTypeError: status.HTTP_409_CONFLICT,
        ChannelAvatarSizeTooBigError: status.HTTP_409_CONFLICT,
        ChannelAvatarAlreadySetError: status.HTTP_409_CONFLICT,
        ChannelActivationFailedError: status.HTTP_409_CONFLICT,
        ChannelNotActiveError: status.HTTP_403_FORBIDDEN,
        ChannelNotFoundByIdError: status.HTTP_404_NOT_FOUND,
        ChannelNotFoundBySlugError: status.HTTP_404_NOT_FOUND,
        ChannelAvatarNotFoundError: status.HTTP_404_NOT_FOUND,
        # Auth
        ChannelAlreadyActivatedError: status.HTTP_409_CONFLICT,
        ChannelInvalidEmailUIDError: status.HTTP_400_BAD_REQUEST,
        ChannelInvalidEmailCodeError: status.HTTP_400_BAD_REQUEST,
        ChannelEmailAlreadyAssociatedWithThisAcccountError: status.HTTP_400_BAD_REQUEST,
        IncorrectEmailOrPasswordError: status.HTTP_401_UNAUTHORIZED,
        NotAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
        JWTTokenInvalidError: status.HTTP_401_UNAUTHORIZED,
        JWTTokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        JWTTokenNotFoundError: status.HTTP_404_NOT_FOUND,
        # OAuth
        OAuthInvalidStateError: status.HTTP_400_BAD_REQUEST,
        OAuthInvalidCodeError: status.HTTP_400_BAD_REQUEST,
        OAuthProviderEmailNotVerifiedError: status.HTTP_409_CONFLICT,
        OAuthProviderAlreadyConnectedError: status.HTTP_409_CONFLICT,
        OAuthNoAccountsConnectedError: status.HTTP_404_NOT_FOUND,
        OAuthAccountNotConnectedError: status.HTTP_404_NOT_FOUND,
        OAuthAccountUnableToDisconnectError: status.HTTP_400_BAD_REQUEST,
        OAuthProviderRequestError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        OAuthProviderResponseError: status.HTTP_502_BAD_GATEWAY,
        OAuthProviderReceivedInvalidResponseError: status.HTTP_502_BAD_GATEWAY,
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
        # Playlists
        VideoAlreadyAddedToPlaylistError: status.HTTP_409_CONFLICT,
        PlaylistAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PlaylistNotFoundError: status.HTTP_404_NOT_FOUND,
        VideoNotFoundInPlaylistError: status.HTTP_404_NOT_FOUND,
        # Posts
        PostAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post reactions
        PostReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post comment
        PostCommentAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostCommentNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post comment reactions
        PostCommentReactionNotFoundError: status.HTTP_404_NOT_FOUND,
        # Subscriptions
        SubscriptionAlreadyExistsError: status.HTTP_409_CONFLICT,
        SelfSubscriptionError: status.HTTP_409_CONFLICT,
        SubscriptionNotFoundError: status.HTTP_404_NOT_FOUND,
    }
    return exception_codes.get(type(exc), status.HTTP_500_INTERNAL_SERVER_ERROR)


def get_exeptions_chain(exc: AppException) -> list:
    exceptions = []

    current_exc: BaseException | None = exc.__cause__

    while current_exc is not None:
        if not isinstance(current_exc, AppException):
            break

        exc_data = {
            'name': type(current_exc).__name__,
            'message': current_exc.message,
            'meta': asdict(current_exc),
        }
        exceptions.append(exc_data)
        current_exc = current_exc.__cause__

    return exceptions


async def exception_handler(
    _: Request,
    exc: AppException,
) -> MsgSpecJSONResponse:
    logger.error(
        msg=exc.message,
        extra={
            'log_meta': asdict(exc),
            'exceptions': get_exeptions_chain(exc=exc),
        },
    )
    return MsgSpecJSONResponse(
        content={'detail': exc.message},
        status_code=get_http_status_code(exc=exc),
    )
