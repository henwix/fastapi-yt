from fastapi import status

from app.domain.common.exceptions.base import AppError
from app.domain.files_cleanup.exceptions import FileCleanupAlreadyCreatedError


def init_files_cleanup() -> dict[type[AppError], int]:
    return {
        FileCleanupAlreadyCreatedError: status.HTTP_409_CONFLICT,
    }
