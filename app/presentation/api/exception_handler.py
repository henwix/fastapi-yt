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
    ChannelNotActiveError,
    ChannelNotFoundBySlugError,
    ChannelNotFoundError,
    ChannelWithEmailAlreadyExists,
    ChannelWithSlugAlreadyExists,
)
from app.domain.common.exceptions import AppException
from app.domain.post_reactions.exceptions import PostReactionAlreadyExists, PostReactionNotFound
from app.domain.posts.exceptions import PostAccessForbiddenError, PostNotFoundError
from app.domain.subscriptions.exceptions import (
    SelfSubscriptionError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)
from app.presentation.api.responses.msgspec import MsgSpecJSONResponse

logger = getLogger(__name__)


def get_http_status_code(exc: AppException):
    exception_codes: dict[type[AppException], int] = {
        # Channels
        ChannelWithEmailAlreadyExists: status.HTTP_400_BAD_REQUEST,
        ChannelWithSlugAlreadyExists: status.HTTP_400_BAD_REQUEST,
        ChannelNotFoundError: status.HTTP_404_NOT_FOUND,
        ChannelNotFoundBySlugError: status.HTTP_404_NOT_FOUND,
        ChannelNotActiveError: status.HTTP_403_FORBIDDEN,
        # Auth
        IncorrectEmailOrPasswordError: status.HTTP_401_UNAUTHORIZED,
        JWTInvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        JWTExpiredTokenError: status.HTTP_401_UNAUTHORIZED,
        NotAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
        # Posts
        PostAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PostNotFoundError: status.HTTP_404_NOT_FOUND,
        # Post reactions
        PostReactionAlreadyExists: status.HTTP_400_BAD_REQUEST,
        PostReactionNotFound: status.HTTP_404_NOT_FOUND,
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
