from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class SubscriptionAlreadyExistsError(AppException):
    message = 'Subscription already exists'

    subscriber_id: UUID
    subscribed_to_id: UUID


@dataclass(kw_only=True)
class SubscriptionNotFoundError(AppException):
    message = 'Subscription not found'

    subscriber_id: UUID
    subscribed_to_id: UUID


@dataclass(kw_only=True)
class SelfSubscriptionError(AppException):
    message = 'You cannot subscribe to yourself'

    subscriber_id: UUID
