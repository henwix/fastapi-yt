from dataclasses import dataclass
from uuid import UUID


@dataclass
class AppException(Exception):
    message = 'Application exception occured'


@dataclass
class InvalidCursorError(AppException):
    message = 'Invalid cursor value'
    cursor: str
    exc_details: str


@dataclass(kw_only=True)
class S3RequestError(AppException):
    message = 'Error occured during S3 request'
    error_code: str
    error_message: str


@dataclass(kw_only=True)
class S3FileNotFoundError(AppException):
    message = 'File not found in S3 storage'
    key: str


@dataclass(kw_only=True)
class S3FileAccessForbiddenError(AppException):
    message = 'File access forbidden'
    channel_id: UUID
    key: str


@dataclass(kw_only=True)
class S3UnavailableError(AppException):
    message = 'S3 storage unavailable'
    exc_details: str
