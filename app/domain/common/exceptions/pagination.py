from dataclasses import dataclass

from app.domain.common.exceptions.base import AppException


@dataclass
class InvalidCursorError(AppException):
    message = 'Invalid cursor value'
    cursor: str
    exc_details: str
