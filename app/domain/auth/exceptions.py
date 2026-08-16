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
class ChannelActivationInvalidIdError(AppException):
    message = 'Invalid channel_id value'
    channel_id: str
    exc_details: str


@dataclass(kw_only=True)
class ChannelActivationInvalidCodeError(AppException):
    message = 'Invalid activation code'
    channel_id: UUID
    code: str
    reason: str
