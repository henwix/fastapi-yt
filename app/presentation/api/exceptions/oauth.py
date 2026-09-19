from fastapi import status

from app.domain.common.exceptions.base import AppError
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


def init_oauth() -> dict[type[AppError], int]:
    return {
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
    }
