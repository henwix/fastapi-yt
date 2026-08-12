from uuid import UUID

from pydantic import Field

from app.application.common.sorting import SortingOrderEnum
from app.application.post_comments.queries import PostCommentsSortingFieldsEnum
from app.domain.post_comments.constants import POST_COMMENT_TEXT_MAX_LENGTH, POST_COMMENT_TEXT_MIN_LENGTH
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreatePostCommentInSchema(BaseSchema):
    text: str = Field(min_length=POST_COMMENT_TEXT_MIN_LENGTH, max_length=POST_COMMENT_TEXT_MAX_LENGTH)
    reply_comment_id: UUID | None = None


class UpdatePostCommentInSchema(BaseUpdateSchema):
    text: str = Field(default='', min_length=POST_COMMENT_TEXT_MIN_LENGTH, max_length=POST_COMMENT_TEXT_MAX_LENGTH)


class PostCommentsSortingParams(BaseSchema):
    sort_by: PostCommentsSortingFieldsEnum = PostCommentsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
