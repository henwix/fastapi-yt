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
class ChannelAvatarInvalidFormatError(AppException):
    message = 'This file format is not allowed for Channel avatars'
    filename: str


@dataclass(kw_only=True)
class ChannelAvatarNotFoundError(AppException):
    message = 'Channel avatar not found'
    channel_id: UUID
