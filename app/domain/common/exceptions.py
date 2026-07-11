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
    error_code: str | None
    error_message: str | None
    error_status: int | None


@dataclass(kw_only=True)
class S3ObjectNotFoundError(AppException):
    message = 'Object not found in S3'
    key: str


@dataclass(kw_only=True)
class S3MultipartUploadNotFoundError(AppException):
    message = 'Multipart upload not found in S3'
    bucket: str
    key: str
    upload_id: str


@dataclass(kw_only=True)
class S3MultipartUploadInvalidPartsError(AppException):
    message = 'Multipart upload invalid parts'
    bucket: str
    key: str
    upload_id: str


@dataclass(kw_only=True)
class S3ObjectAccessForbiddenError(AppException):
    message = 'S3 object access forbidden'
    channel_id: UUID
    key: str


@dataclass(kw_only=True)
class S3UnavailableError(AppException):
    message = 'S3 unavailable'
    exc_details: str
