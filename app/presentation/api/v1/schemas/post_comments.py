from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl

from app.application.common.sorting import SortingOrderEnum
from app.application.post_comments.dto import DetailedPostCommentDTO
from app.application.post_comments.queries import PostCommentsSortingFieldsEnum
from app.domain.post_comments.entities import PostComment
from app.domain.post_comments.enums import PostCommentReplyLevelEnum
from app.domain.posts.constants import POST_COMMENT_TEXT_MAX_LENGTH, POST_COMMENT_TEXT_MIN_LENGTH
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class PostCommentOutSchema(BaseSchema):
    id: UUID
    text: str
    reply_level: PostCommentReplyLevelEnum
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
    reply_level: PostCommentReplyLevelEnum
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime
    author_slug: str

    @staticmethod
    def from_dto(dto: DetailedPostCommentDTO) -> DetailedPostCommentOutSchema:
        return DetailedPostCommentOutSchema(
            id=dto.id,
            text=dto.text,
            reply_level=dto.reply_level,
            is_edited=dto.is_edited,
            reply_comment_id=dto.reply_comment_id,
            created_at=dto.created_at,
            author_slug=dto.author_slug,
        )


class CreatePostCommentInSchema(BaseSchema):
    text: str = Field(min_length=POST_COMMENT_TEXT_MIN_LENGTH, max_length=POST_COMMENT_TEXT_MAX_LENGTH)
    reply_comment_id: UUID | None = None


class UpdatePostCommentInSchema(BaseUpdateSchema):
    text: str = Field(default='', min_length=POST_COMMENT_TEXT_MIN_LENGTH, max_length=POST_COMMENT_TEXT_MAX_LENGTH)


class PostCommentsSortingParams(BaseSchema):
    sort_by: PostCommentsSortingFieldsEnum = PostCommentsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class PostCommentsCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[DetailedPostCommentOutSchema]
