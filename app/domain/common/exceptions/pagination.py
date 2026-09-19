from dataclasses import dataclass

from app.domain.common.exceptions.base import AppError


@dataclass
class InvalidCursorError(AppError):
    message = 'Invalid cursor value'
    cursor: str
    exc_details: str
