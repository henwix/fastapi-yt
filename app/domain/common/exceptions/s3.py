from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class S3ObjectNotFoundError(AppError):
    message = 'Object not found in S3'
    key: str
    action: str


@dataclass(kw_only=True)
class S3MultipartUploadNotFoundError(AppError):
    message = 'Multipart upload not found in S3'
    bucket: str
    key: str
    upload_id: str


@dataclass(kw_only=True)
class S3MultipartUploadInvalidPartsError(AppError):
    message = 'Multipart upload invalid parts'
    bucket: str
    key: str
    upload_id: str


@dataclass(kw_only=True)
class S3ObjectAccessForbiddenError(AppError):
    message = 'S3 object access forbidden'
    channel_id: UUID
    key: str


@dataclass(kw_only=True)
class S3RequestError(AppError):
    message = 'Error occured during S3 request'
    exc_details: str


@dataclass(kw_only=True)
class S3ResponseError(AppError):
    message = 'Error occured in S3 response'
    error_code: str | None
    error_message: str | None
    error_status: int | None
