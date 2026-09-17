from dataclasses import dataclass
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum


@dataclass(kw_only=True, frozen=True)
class CreateVideoCommentReactionCommand:
    current_channel_id: UUID
    video_comment_id: UUID
    reaction_type: ReactionTypeEnum


@dataclass(kw_only=True, frozen=True)
class DeleteVideoCommentReactionCommand:
    current_channel_id: UUID
    video_comment_id: UUID
