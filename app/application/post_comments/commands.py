from dataclasses import dataclass
from uuid import UUID

from app.domain.common.constants import Empty


@dataclass(kw_only=True, frozen=True)
class CreatePostCommentCommand:
    current_channel_id: UUID
    post_id: UUID
    text: str
    reply_comment_id: UUID | Empty = Empty.UNSET


@dataclass(kw_only=True, frozen=True)
class DeletePostCommentCommand:
    current_channel_id: UUID
    post_comment_id: UUID


@dataclass(kw_only=True, frozen=True)
class UpdatePostCommentCommand:
    current_channel_id: UUID
    post_comment_id: UUID
    text: str | Empty = Empty.UNSET
