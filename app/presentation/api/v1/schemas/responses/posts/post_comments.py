from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from app.application.posts.dto import DetailedPostComment
from app.domain.posts.entities import PostComment
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
    channel_slug: str
    channel_avatar_url: HttpUrl | None

    @staticmethod
    def from_dto(dto: DetailedPostComment) -> DetailedPostCommentOutSchema:
        return DetailedPostCommentOutSchema(
            id=dto.id,
            text=dto.text,
            reply_level=dto.reply_level,
            is_edited=dto.is_edited,
            reply_comment_id=dto.reply_comment_id,
            created_at=dto.created_at,
            channel_slug=dto.channel_slug,
            channel_avatar_url=dto.channel_avatar_url,
        )
