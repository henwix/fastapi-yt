from datetime import datetime
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum
from app.domain.post_comment_reactions.entities import PostCommentReaction
from app.presentation.api.v1.schemas.base import BaseSchema


class CreatePostCommentReactionInSchema(BaseSchema):
    reaction_type: ReactionTypeEnum


class PostCommentReactionOutSchema(BaseSchema):
    post_comment_id: UUID
    reaction_type: ReactionTypeEnum
    created_at: datetime

    @staticmethod
    def from_entity(entity: PostCommentReaction) -> PostCommentReactionOutSchema:
        return PostCommentReactionOutSchema(
            post_comment_id=entity.post_comment_id,
            reaction_type=entity.reaction_type,
            created_at=entity.created_at,
        )
