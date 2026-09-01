from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException
from app.domain.oauth.enums import OAuthProviderEnum


@dataclass(kw_only=True)
class OAuthInvalidStateError(AppException):
    message = 'Invalid state'
    provider: OAuthProviderEnum
    state: str | None


@dataclass(kw_only=True)
class OAuthInvalidCodeError(AppException):
    message = 'Invalid code'
    provider: OAuthProviderEnum
    code: str


@dataclass(kw_only=True)
class OAuthProviderEmailNotVerifiedError(AppException):
    message = 'OAuth provider email not verified'
    provider: OAuthProviderEnum


@dataclass(kw_only=True)
class OAuthProviderAlreadyConnectedError(AppException):
    message = 'OAuth provider already connected'
    channel_id: UUID
    provider: OAuthProviderEnum


@dataclass(kw_only=True)
class OAuthProviderNotSupportedError(AppException):
    message = 'OAuth provider not supported'


@dataclass(kw_only=True)
class OAuthNoAccountsConnectedError(AppException):
    message = 'No connected OAuth accounts were found'
    channel_id: UUID


@dataclass(kw_only=True)
class OAuthAccountNotConnectedError(AppException):
    message = 'OAuth account not connected'
    channel_id: UUID
    provider: OAuthProviderEnum


@dataclass(kw_only=True)
class OAuthAccountUnableToDisconnectError(AppException):
    message = 'OAuth account cannot be disconnected'
    channel_id: UUID
    provider: OAuthProviderEnum


@dataclass(kw_only=True)
class OAuthProviderRequestError(AppException):
    message = 'Exception occured during OAuth provider request'
    provider: OAuthProviderEnum
    error: str


@dataclass(kw_only=True)
class OAuthProviderResponseError(AppException):
    message = 'Invalid response received from OAuth provider'
    provider: OAuthProviderEnum
    error: str
