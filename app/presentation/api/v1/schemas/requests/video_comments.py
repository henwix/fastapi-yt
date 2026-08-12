from uuid import UUID

from pydantic import Field

from app.application.common.sorting import SortingOrderEnum
from app.application.video_comments.queries import VideoCommentsSortingFieldsEnum
from app.domain.video_comments.constants import VIDEO_COMMENT_TEXT_MAX_LENGTH, VIDEO_COMMENT_TEXT_MIN_LENGTH
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreateVideoCommentInSchema(BaseSchema):
    text: str = Field(min_length=VIDEO_COMMENT_TEXT_MIN_LENGTH, max_length=VIDEO_COMMENT_TEXT_MAX_LENGTH)
    reply_comment_id: UUID | None = None


class UpdateVideoCommentInSchema(BaseUpdateSchema):
    text: str = Field(default='', min_length=VIDEO_COMMENT_TEXT_MIN_LENGTH, max_length=VIDEO_COMMENT_TEXT_MAX_LENGTH)


class VideoCommentsSortingParams(BaseSchema):
    sort_by: VideoCommentsSortingFieldsEnum = VideoCommentsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
