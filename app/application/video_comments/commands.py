from dataclasses import dataclass
from uuid import UUID

from app.domain.common.constants import Empty


@dataclass(kw_only=True, frozen=True)
class CreateVideoCommentCommand:
    current_channel_id: UUID
    video_id: str
    text: str
    reply_comment_id: UUID | Empty = Empty.UNSET


@dataclass(kw_only=True, frozen=True)
class DeleteVideoCommentCommand:
    current_channel_id: UUID
    video_comment_id: UUID


@dataclass(kw_only=True, frozen=True)
class UpdateVideoCommentCommand:
    current_channel_id: UUID
    video_comment_id: UUID
    text: str | Empty = Empty.UNSET
