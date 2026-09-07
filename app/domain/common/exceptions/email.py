from dataclasses import dataclass

from app.domain.common.exceptions.base import AppException


@dataclass(kw_only=True)
class EmailSendingError(AppException):
    message = 'Error occured during SMTP email sending'
    exc_details: str
