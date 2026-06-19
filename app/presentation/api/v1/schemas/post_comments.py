from datetime import datetime
from uuid import UUID

from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.enums import PostCommentReplyLevelEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class PostCommentSchema(BaseSchema):
    id: UUID
    text: str
    reply_level: PostCommentReplyLevelEnum
    reply_comment_id: UUID | None
    created_at: datetime

    @staticmethod
    def from_entity(entity: PostComment) -> PostCommentSchema:
        return PostCommentSchema(
            id=entity.id,
            text=entity.text,
            reply_level=entity.reply_level,
            reply_comment_id=entity.reply_comment_id,
            created_at=entity.created_at,
        )


class CreatePostCommentSchema(BaseSchema):
    text: str
    reply_comment_id: UUID | None = None
