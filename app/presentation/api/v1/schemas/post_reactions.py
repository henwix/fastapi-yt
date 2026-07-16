from datetime import datetime
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum
from app.domain.post_reactions.entities import PostReaction
from app.presentation.api.v1.schemas.base import BaseSchema


class CreatePostReactionInSchema(BaseSchema):
    reaction_type: ReactionTypeEnum


class PostReactionOutSchema(BaseSchema):
    post_id: UUID
    reaction_type: ReactionTypeEnum
    created_at: datetime

    @staticmethod
    def from_entity(entity: PostReaction) -> PostReactionOutSchema:
        return PostReactionOutSchema(
            post_id=entity.post_id,
            reaction_type=entity.reaction_type,
            created_at=entity.created_at,
        )
