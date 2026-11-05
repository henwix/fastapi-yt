from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class ChannelSlugAlreadyExistsError(AppError):
    message = 'Channel with this slug already exists'
    channel_slug: str


@dataclass(kw_only=True)
class ChannelEmailAlreadyExistsError(AppError):
    message = 'Channel with this email already exists'
    channel_email: str


@dataclass(kw_only=True)
class ChannelEmailInvalidFormatError(AppError):
    message = 'Invalid email format'
    pattern: str
    email: str


@dataclass(kw_only=True)
class ChannelEmailTooLongError(AppError):
    message = 'Email too long'
    email: str
    email_max_length: int


@dataclass(kw_only=True)
class ChannelSlugInvalidFormatError(AppError):
    message = 'Invalid slug format'
    pattern: str
    slug: str


@dataclass(kw_only=True)
class ChannelNotFoundByIdError(AppError):
    message = 'Channel not found by id'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelNotFoundBySlugError(AppError):
    message = 'Channel not found by slug'
    channel_slug: str


@dataclass(kw_only=True)
class ChannelNotActiveError(AppError):
    message = 'Channel not active'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelDeletedError(AppError):
    message = 'Channel deleted'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelNotDeletedError(AppError):
    message = 'Channel not deleted'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelFailedToActivateError(AppError):
    message = 'Failed to active channel'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelFailedToDeleteError(AppError):
    message = 'Failed to delete channel'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelFailedToRestoreError(AppError):
    message = 'Failed to restore channel'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelAvatarNotFoundError(AppError):
    message = 'Channel avatar not found'
    channel_id: UUID
