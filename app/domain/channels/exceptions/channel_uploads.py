from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


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
class ChannelAvatarAlreadySetError(AppError):
    message = 'This Channel avatar is already set'
    channel_id: UUID
    avatar_s3_key: str
