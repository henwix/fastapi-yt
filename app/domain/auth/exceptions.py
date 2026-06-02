from dataclasses import dataclass

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
