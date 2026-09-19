from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class SubscriptionAlreadyExistsError(AppError):
    message = 'Subscription already exists'
    subscriber_id: UUID
    subscribed_to_id: UUID


@dataclass(kw_only=True)
class SubscriptionNotFoundError(AppError):
    message = 'Subscription not found'
    subscriber_id: UUID
    subscribed_to_id: UUID


@dataclass(kw_only=True)
class SelfSubscriptionError(AppError):
    message = 'You cannot subscribe to yourself'
    subscriber_id: UUID
