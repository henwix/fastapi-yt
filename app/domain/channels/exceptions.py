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
class ChannelAvatarSizeTooBigError(AppError):
    message = 'Channel avatar size too big'
    key: str
    file_size: int
    file_max_size: int


@dataclass(kw_only=True)
class ChannelAvatarInvalidKeyError(AppError):
    message = 'Channel avatar invalid key'
    key: str


@dataclass(kw_only=True)
class ChannelAvatarInvalidFilenameError(AppError):
    message = 'Channel avatar invalid filename'
    filename: str


@dataclass(kw_only=True)
class ChannelAvatarInvalidContentTypeError(AppError):
    message = 'Channel avatar invalid content type'
    key: str
    metadata_content_type: str
    actual_content_type: str


@dataclass(kw_only=True)
class ChannelAvatarNotFoundError(AppError):
    message = 'Channel avatar not found'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelAvatarAlreadySetError(AppError):
    message = 'This Channel avatar is already set'
    channel_id: UUID
    avatar_s3_key: str


@dataclass(kw_only=True)
class ChannelActivationFailedError(AppError):
    message = 'Channel activation failed'
    channel_id: UUID
