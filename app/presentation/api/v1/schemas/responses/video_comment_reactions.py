from datetime import datetime
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum
from app.domain.video_comment_reactions.entities import VideoCommentReaction
from app.presentation.api.v1.schemas.base import BaseSchema


class VideoCommentReactionOutSchema(BaseSchema):
    video_comment_id: UUID
    reaction_type: ReactionTypeEnum
    created_at: datetime

    @staticmethod
    def from_entity(entity: VideoCommentReaction) -> VideoCommentReactionOutSchema:
        return VideoCommentReactionOutSchema(
            video_comment_id=entity.video_comment_id,
            reaction_type=entity.reaction_type,
            created_at=entity.created_at,
        )
