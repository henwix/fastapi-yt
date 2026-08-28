from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from app.application.post_comments.dto import DetailedPostComment
from app.domain.post_comments.entities import PostComment
from app.presentation.api.v1.schemas.base import BaseSchema


class PostCommentOutSchema(BaseSchema):
    id: UUID
    text: str
    reply_level: int
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime

    @staticmethod
    def from_entity(entity: PostComment) -> PostCommentOutSchema:
        return PostCommentOutSchema(
            id=entity.id,
            text=entity.text,
            reply_level=entity.reply_level,
            is_edited=entity.is_edited,
            reply_comment_id=entity.reply_comment_id,
            created_at=entity.created_at,
        )


class DetailedPostCommentOutSchema(BaseSchema):
    id: UUID
    text: str
    reply_level: int
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime
    author_slug: str

    @staticmethod
    def from_dto(dto: DetailedPostComment) -> DetailedPostCommentOutSchema:
        return DetailedPostCommentOutSchema(
            id=dto.id,
            text=dto.text,
            reply_level=dto.reply_level,
            is_edited=dto.is_edited,
            reply_comment_id=dto.reply_comment_id,
            created_at=dto.created_at,
            author_slug=dto.author_slug,
        )


class PostCommentsCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[DetailedPostCommentOutSchema]
