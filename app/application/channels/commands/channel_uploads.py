from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class GenerateChannelAvatarUploadUrlCommand:
    current_channel_id: UUID
    filename: str


@dataclass(kw_only=True, frozen=True)
class ConfirmChannelAvatarUploadCommand:
    current_channel_id: UUID
    key: str
