from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppException


@dataclass(kw_only=True)
class ChannelSlugAlreadyExistsError(AppException):
    message = 'Channel with this slug already exists'
    channel_slug: str


@dataclass(kw_only=True)
class ChannelEmailAlreadyExistsError(AppException):
    message = 'Channel with this email already exists'
    channel_email: str


@dataclass(kw_only=True)
class ChannelEmailInvalidFormatError(AppException):
    message = 'Invalid email format'
    pattern: str
    email: str


@dataclass(kw_only=True)
class ChannelEmailTooLongError(AppException):
    message = 'Email too long'
    email: str
    email_max_length: int


@dataclass(kw_only=True)
class ChannelSlugInvalidFormatError(AppException):
    message = 'Invalid slug format'
    pattern: str
    slug: str


@dataclass(kw_only=True)
class ChannelNotFoundByIdError(AppException):
    message = 'Channel not found by id'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelNotFoundBySlugError(AppException):
    message = 'Channel not found by slug'
    channel_slug: str


@dataclass(kw_only=True)
class ChannelNotActiveError(AppException):
    message = 'Channel not active'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelAvatarSizeTooBigError(AppException):
    message = 'Channel avatar size too big'
    key: str
    file_size: int
    file_max_size: int


@dataclass(kw_only=True)
class ChannelAvatarInvalidKeyError(AppException):
    message = 'Channel avatar invalid key'
    key: str


@dataclass(kw_only=True)
class ChannelAvatarInvalidFilenameError(AppException):
    message = 'Channel avatar invalid filename'
    filename: str


@dataclass(kw_only=True)
class ChannelAvatarInvalidContentTypeError(AppException):
    message = 'Channel avatar invalid content type'
    key: str
    metadata_content_type: str
    actual_content_type: str


@dataclass(kw_only=True)
class ChannelAvatarNotFoundError(AppException):
    message = 'Channel avatar not found'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelAvatarAlreadySetError(AppException):
    message = 'This Channel avatar is already set'
    channel_id: UUID
    avatar_s3_key: str


@dataclass(kw_only=True)
class ChannelActivationFailedError(AppException):
    message = 'Channel activation failed'
    channel_id: UUID
