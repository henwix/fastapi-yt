from fastapi import status

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
from app.domain.common.exceptions.base import AppError


def init_auth() -> dict[type[AppError], int]:
    return {
        ChannelAlreadyActivatedError: status.HTTP_409_CONFLICT,
        ChannelInvalidEmailUIDError: status.HTTP_400_BAD_REQUEST,
        ChannelInvalidEmailCodeError: status.HTTP_400_BAD_REQUEST,
        ChannelEmailAlreadyAssociatedWithThisAcccountError: status.HTTP_409_CONFLICT,
        IncorrectEmailOrPasswordError: status.HTTP_401_UNAUTHORIZED,
        NotAuthenticatedError: status.HTTP_401_UNAUTHORIZED,
        JWTTokenInvalidError: status.HTTP_401_UNAUTHORIZED,
        JWTTokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        JWTTokenNotFoundError: status.HTTP_404_NOT_FOUND,
    }
