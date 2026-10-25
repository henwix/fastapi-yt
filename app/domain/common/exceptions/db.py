from dataclasses import dataclass

from app.domain.common.exceptions.base import AppError


@dataclass
class TransactionRollbackError(AppError):
    message = 'Transaction error'
