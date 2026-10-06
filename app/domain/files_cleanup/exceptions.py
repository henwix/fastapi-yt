from dataclasses import dataclass

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class FileCleanupAlreadyCreatedError(AppError):
    message = 'File cleanup for this object already created'
    s3_key: str
    bucket: str
