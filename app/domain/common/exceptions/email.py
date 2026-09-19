from dataclasses import dataclass

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class EmailSendingError(AppError):
    message = 'Error occured during SMTP email sending'
    exc_details: str
