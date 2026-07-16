from dataclasses import dataclass
from uuid import UUID

from app.domain.common.constants import Empty


@dataclass(kw_only=True, frozen=True)
class CreateChannelCommand:
    email: str
    name: str
    slug: str
    description: str
    country: str
    password: str


@dataclass(kw_only=True, frozen=True)
class UpdateChannelCommand:
    current_channel_id: UUID
    name: str | Empty = Empty.UNSET
    slug: str | Empty = Empty.UNSET
    description: str | Empty = Empty.UNSET
    country: str | Empty = Empty.UNSET


@dataclass(kw_only=True, frozen=True)
class DeleteChannelCommand:
    current_channel_id: UUID


@dataclass(kw_only=True, frozen=True)
class SetChannelPasswordCommand:
    current_channel_id: UUID
    new_password: str


@dataclass(kw_only=True, frozen=True)
class GenerateChannelAvatarUploadUrlCommand:
    current_channel_id: UUID
    filename: str


@dataclass(kw_only=True, frozen=True)
class ConfirmChannelAvatarUploadCommand:
    current_channel_id: UUID
    key: str


@dataclass(kw_only=True, frozen=True)
class DeleteChannelAvatarCommand:
    current_channel_id: UUID
