from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class ChannelWithSlugAlreadyExistsError(AppException):
    message = 'Channel with this slug already exists'
    slug: str


@dataclass(kw_only=True)
class ChannelWithEmailAlreadyExistsError(AppException):
    message = 'Channel with this email already exists'
    email: str


@dataclass(kw_only=True)
class ChannelNotFoundByIdError(AppException):
    message = 'Channel not found by id'
    id: UUID


@dataclass(kw_only=True)
class ChannelNotFoundBySlugError(AppException):
    message = 'Channel not found by slug'
    slug: str


@dataclass(kw_only=True)
class ChannelNotActiveError(AppException):
    message = 'Channel not active'
    id: UUID


@dataclass(kw_only=True)
class ChannelAvatarInvalidFileFormatError(AppException):
    message = 'Channel avatar invalid file format'
    file: str


@dataclass(kw_only=True)
class ChannelAvatarInvalidKeyError(AppException):
    message = 'Channel avatar invalid key'
    key: str


@dataclass(kw_only=True)
class ChannelAvatarInvalidFileContentTypeError(AppException):
    message = 'Channel avatar invalid content type'
    key: str
    content_type: str


@dataclass(kw_only=True)
class ChannelAvatarNotFoundError(AppException):
    message = 'Channel avatar not found'
    channel_id: UUID


@dataclass(kw_only=True)
class ChannelAvatarAlreadySetError(AppException):
    message = 'This Channel avatar is already set'
    channel_id: UUID
    avatar_s3_key: str
