from datetime import datetime
from uuid import UUID

from app.domain.common.enums import ReactionTypeEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class CreatePostCommentReactionSchema(BaseSchema):
    reaction_type: ReactionTypeEnum


class PostCommentReactionSchema(BaseSchema):
    post_comment_id: UUID
    reaction_type: ReactionTypeEnum
    created_at: datetime
