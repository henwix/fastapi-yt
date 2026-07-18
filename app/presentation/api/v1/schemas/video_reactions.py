from datetime import datetime

from app.domain.common.enums import ReactionTypeEnum
from app.domain.video_reactions.entities import VideoReaction
from app.presentation.api.v1.schemas.base import BaseSchema


class CreateVideoReactionInSchema(BaseSchema):
    reaction_type: ReactionTypeEnum


class VideoReactionOutSchema(BaseSchema):
    video_id: str
    reaction_type: ReactionTypeEnum
    created_at: datetime

    @staticmethod
    def from_entity(entity: VideoReaction) -> VideoReactionOutSchema:
        return VideoReactionOutSchema(
            video_id=entity.video_id,
            reaction_type=entity.reaction_type,
            created_at=entity.created_at,
        )
