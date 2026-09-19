from fastapi import status

from app.domain.common.exceptions.base import AppError
from app.domain.common.exceptions.pagination import InvalidCursorError
from app.domain.common.exceptions.s3 import (
    S3MultipartUploadInvalidPartsError,
    S3MultipartUploadNotFoundError,
    S3ObjectAccessForbiddenError,
    S3ObjectNotFoundError,
    S3RequestError,
    S3ResponseError,
)


def init_common() -> dict[type[AppError], int]:
    return {
        InvalidCursorError: status.HTTP_400_BAD_REQUEST,
        S3ObjectAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        S3ObjectNotFoundError: status.HTTP_404_NOT_FOUND,
        S3MultipartUploadNotFoundError: status.HTTP_404_NOT_FOUND,
        S3MultipartUploadInvalidPartsError: status.HTTP_400_BAD_REQUEST,
        S3RequestError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        S3ResponseError: status.HTTP_502_BAD_GATEWAY,
    }
