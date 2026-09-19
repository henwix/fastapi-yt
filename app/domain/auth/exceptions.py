from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass
class IncorrectEmailOrPasswordError(AppError):
    message = 'Incorrect email or password'


@dataclass(kw_only=True)
class JWTTokenInvalidError(AppError):
    message = 'JWT token is invalid'
    error_detail: str


@dataclass
class JWTTokenExpiredError(AppError):
    message = 'JWT token is expired'


@dataclass
class JWTTokenNotFoundError(AppError):
    message = 'JWT token not found'


@dataclass
class NotAuthenticatedError(AppError):
    message = 'Not authenticated'


@dataclass(kw_only=True)
class ChannelAlreadyActivatedError(AppError):
    message = 'Channel already activated'


@dataclass(kw_only=True)
class ChannelEmailAlreadyAssociatedWithThisAcccountError(AppError):
    message = 'Email already associated with this account'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelInvalidEmailUIDError(AppError):
    message = 'Invalid uid'
    uid: str
    exc_details: str


@dataclass(kw_only=True)
class ChannelInvalidEmailCodeError(AppError):
    message = 'Invalid code'
    channel_id: UUID
    code: str
    reason: str
