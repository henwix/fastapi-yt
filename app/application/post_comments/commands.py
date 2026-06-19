from dataclasses import dataclass
from uuid import UUID

from app.domain.common.constants import Empty


@dataclass(kw_only=True, frozen=True)
class CreatePostCommentCommand:
    current_channel_id: UUID
    post_id: UUID
    text: str
    reply_comment_id: UUID | Empty = Empty.UNSET
