from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass
class IncorrectEmailOrPasswordError(AppException):
    message = 'Incorrect email or password'


@dataclass(kw_only=True)
class JWTInvalidTokenError(AppException):
    message = 'JWT token is invalid'
    error_detail: str


@dataclass
class JWTExpiredTokenError(AppException):
    message = 'JWT token is expired'


@dataclass
class NotAuthenticatedError(AppException):
    message = 'Not authenticated'


@dataclass(kw_only=True)
class ChannelAlreadyActivatedError(AppException):
    message = 'Channel already activated'


@dataclass(kw_only=True)
class ChannelEmailAlreadyAssociatedWithThisAcccountError(AppException):
    message = 'Email already associated with this account'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelInvalidEmailUIDError(AppException):
    message = 'Invalid uid'
    uid: str
    exc_details: str


@dataclass(kw_only=True)
class ChannelInvalidEmailCodeError(AppException):
    message = 'Invalid code'
    channel_id: UUID
    code: str
    reason: str
