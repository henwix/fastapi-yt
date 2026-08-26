from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException
from app.domain.oauth.enums import OAuthProvidersEnum


@dataclass(kw_only=True)
class OAuthInvalidStateError(AppException):
    message = 'Invalid state'
    provider: OAuthProvidersEnum
    state: str | None


@dataclass(kw_only=True)
class OAuthInvalidCodeError(AppException):
    message = 'Invalid code'
    provider: OAuthProvidersEnum
    code: str


@dataclass(kw_only=True)
class OAuthProviderEmailNotVerifiedError(AppException):
    message = 'OAuth provider email not verified'
    provider: OAuthProvidersEnum


@dataclass(kw_only=True)
class OAuthProviderUidNotFoundError(AppException):
    message = 'OAuth provider uid not found'
    provider: OAuthProvidersEnum


@dataclass(kw_only=True)
class OAuthProviderEmailNotFoundError(AppException):
    message = 'OAuth provider email not found'
    provider: OAuthProvidersEnum


@dataclass(kw_only=True)
class OAuthProviderAlreadyConnectedError(AppException):
    message = 'OAuth provider already connected'
    current_channel_id: UUID
    provider: OAuthProvidersEnum


@dataclass(kw_only=True)
class OAuthProviderRequestError(AppException):
    message = 'Exception occured during OAuth provider request'
    provider: OAuthProvidersEnum
    error: str
