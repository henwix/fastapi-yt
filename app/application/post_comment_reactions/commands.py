from dataclasses import dataclass
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum


@dataclass(kw_only=True, frozen=True)
class CreatePostCommentReactionCommand:
    current_channel_id: UUID
    post_comment_id: UUID
    reaction_type: ReactionTypeEnum


@dataclass(kw_only=True, frozen=True)
class DeletePostCommentReactionCommand:
    current_channel_id: UUID
    post_comment_id: UUID
