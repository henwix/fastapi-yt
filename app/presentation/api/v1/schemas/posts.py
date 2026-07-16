from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.application.common.sorting import SortingOrderEnum
from app.application.posts.dto import DetailedPostDTO
from app.application.posts.queries import PostsSortingFieldsEnum
from app.domain.posts.constants import POST_TEXT_MAX_LENGTH, POST_TEXT_MIN_LENGTH
from app.domain.posts.entities import Post
from app.presentation.api.v1.schemas.base import BaseCursorResponse, BaseSchema, BaseUpdateSchema


class CreatePostInSchema(BaseSchema):
    text: str = Field(min_length=POST_TEXT_MIN_LENGTH, max_length=POST_TEXT_MAX_LENGTH)


class UpdatePostInSchema(BaseUpdateSchema):
    text: str = Field(default='', min_length=POST_TEXT_MIN_LENGTH, max_length=POST_TEXT_MAX_LENGTH)


class PostOutSchema(BaseSchema):
    id: UUID
    text: str
    created_at: datetime

    @staticmethod
    def from_entity(entity: Post) -> PostOutSchema:
        return PostOutSchema(
            id=entity.id,
            text=entity.text,
            created_at=entity.created_at,
        )


class DetailedPostOutSchema(BaseSchema):
    id: UUID
    text: str
    created_at: datetime
    channel_name: str
    channel_slug: str

    @staticmethod
    def from_dto(dto: DetailedPostDTO) -> DetailedPostOutSchema:
        return DetailedPostOutSchema(
            id=dto.id,
            text=dto.text,
            created_at=dto.created_at,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
        )


class PostsSortingParams(BaseSchema):
    sort_by: PostsSortingFieldsEnum = PostsSortingFieldsEnum.CREATED_AT
    order: SortingOrderEnum = SortingOrderEnum.DESC


class PostsCursorResponse(BaseCursorResponse):
    results: list[DetailedPostOutSchema]
