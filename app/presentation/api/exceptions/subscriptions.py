from fastapi import status

from app.domain.common.exceptions.base import AppError
from app.domain.subscriptions.exceptions import (
    SelfSubscriptionError,
    SubscriptionAlreadyExistsError,
    SubscriptionNotFoundError,
)


def init_subscriptions() -> dict[type[AppError], int]:
    return {
        SubscriptionAlreadyExistsError: status.HTTP_409_CONFLICT,
        SelfSubscriptionError: status.HTTP_409_CONFLICT,
        SubscriptionNotFoundError: status.HTTP_404_NOT_FOUND,
    }
