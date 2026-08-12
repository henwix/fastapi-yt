from pydantic import Field

from app.application.common.sorting import SortingOrderEnum
from app.application.posts.queries import PostsSortingFieldsEnum
from app.domain.posts.constants import POST_TEXT_MAX_LENGTH, POST_TEXT_MIN_LENGTH
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreatePostInSchema(BaseSchema):
    text: str = Field(min_length=POST_TEXT_MIN_LENGTH, max_length=POST_TEXT_MAX_LENGTH)


class UpdatePostInSchema(BaseUpdateSchema):
    text: str = Field(default='', min_length=POST_TEXT_MIN_LENGTH, max_length=POST_TEXT_MAX_LENGTH)


class PostsSortingParams(BaseSchema):
    sort_by: PostsSortingFieldsEnum = PostsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC
