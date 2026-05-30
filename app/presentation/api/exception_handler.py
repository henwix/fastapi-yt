from dataclasses import asdict
from logging import getLogger

from fastapi import Request, status

from app.domain.auth.exceptions import IncorrectEmailOrPasswordError, JWTExpiredTokenError, JWTInvalidTokenError
from app.domain.channels.exceptions import ChannelWithEmailAlreadyExists, ChannelWithSlugAlreadyExists
from app.domain.common.exceptions import AppException
from app.presentation.api.responses.msgspec import MsgSpecJSONResponse

logger = getLogger(__name__)


def get_http_status_code(exc: AppException):
    exception_codes: dict[type[AppException], int] = {
        # Channels
        ChannelWithEmailAlreadyExists: status.HTTP_400_BAD_REQUEST,
        ChannelWithSlugAlreadyExists: status.HTTP_400_BAD_REQUEST,
        # Auth
        IncorrectEmailOrPasswordError: status.HTTP_401_UNAUTHORIZED,
        JWTInvalidTokenError: status.HTTP_401_UNAUTHORIZED,
        JWTExpiredTokenError: status.HTTP_401_UNAUTHORIZED,
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
