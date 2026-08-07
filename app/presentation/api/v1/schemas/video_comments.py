from datetime import datetime
from uuid import UUID

from pydantic import Field, HttpUrl

from app.application.common.sorting import SortingOrderEnum
from app.application.video_comments.dto import DetailedVideoCommentDTO
from app.application.video_comments.queries import VideoCommentsSortingFieldsEnum
from app.domain.video_comments.constants import VIDEO_COMMENT_TEXT_MAX_LENGTH, VIDEO_COMMENT_TEXT_MIN_LENGTH
from app.domain.video_comments.entities import VideoComment
from app.domain.video_comments.enums import VideoCommentReplyLevelEnum
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreateVideoCommentInSchema(BaseSchema):
    text: str = Field(min_length=VIDEO_COMMENT_TEXT_MIN_LENGTH, max_length=VIDEO_COMMENT_TEXT_MAX_LENGTH)
    reply_comment_id: UUID | None = None


class UpdateVideoCommentInSchema(BaseUpdateSchema):
    text: str = Field(default='', min_length=VIDEO_COMMENT_TEXT_MIN_LENGTH, max_length=VIDEO_COMMENT_TEXT_MAX_LENGTH)


class VideoCommentOutSchema(BaseSchema):
    id: UUID
    text: str
    reply_level: VideoCommentReplyLevelEnum
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime

    @staticmethod
    def from_entity(entity: VideoComment) -> VideoCommentOutSchema:
        return VideoCommentOutSchema(
            id=entity.id,
            text=entity.text,
            reply_level=entity.reply_level,
            is_edited=entity.is_edited,
            reply_comment_id=entity.reply_comment_id,
            created_at=entity.created_at,
        )


class DetailedVideoCommentOutSchema(BaseSchema):
    id: UUID
    text: str
    reply_level: VideoCommentReplyLevelEnum
    is_edited: bool
    reply_comment_id: UUID | None
    created_at: datetime
    author_slug: str

    @staticmethod
    def from_dto(dto: DetailedVideoCommentDTO) -> DetailedVideoCommentOutSchema:
        return DetailedVideoCommentOutSchema(
            id=dto.id,
            text=dto.text,
            reply_level=dto.reply_level,
            is_edited=dto.is_edited,
            reply_comment_id=dto.reply_comment_id,
            created_at=dto.created_at,
            author_slug=dto.author_slug,
        )


class VideoCommentsSortingParams(BaseSchema):
    sort_by: VideoCommentsSortingFieldsEnum = VideoCommentsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class VideoCommentsCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[DetailedVideoCommentOutSchema]
