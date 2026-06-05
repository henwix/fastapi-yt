from dataclasses import dataclass
from uuid import UUID


@dataclass(kw_only=True, frozen=True)
class CreatePostCommand:
    channel_id: UUID
    text: str


@dataclass(kw_only=True, frozen=True)
class UpdatePostCommand:
    channel_id: UUID
    post_id: UUID
    text: str


@dataclass(kw_only=True, frozen=True)
class DeletePostCommand:
    channel_id: UUID
    post_id: UUID
