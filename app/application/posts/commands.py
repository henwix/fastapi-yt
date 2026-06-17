from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class CreatePostCommand:
    current_channel_id: UUID
    text: str


@dataclass(kw_only=True, frozen=True)
class UpdatePostCommand:
    current_channel_id: UUID
    post_id: UUID
    text: str


@dataclass(kw_only=True, frozen=True)
class DeletePostCommand:
    current_channel_id: UUID
    post_id: UUID
