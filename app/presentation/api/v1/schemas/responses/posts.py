from datetime import datetime
from uuid import UUID

from pydantic import HttpUrl

from app.application.posts.dto import DetailedPost
from app.domain.posts.entities import Post
from app.presentation.api.v1.schemas.base import BaseSchema


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
    def from_dto(dto: DetailedPost) -> DetailedPostOutSchema:
        return DetailedPostOutSchema(
            id=dto.id,
            text=dto.text,
            created_at=dto.created_at,
            channel_name=dto.channel_name,
            channel_slug=dto.channel_slug,
        )


class PostsCursorResponse(BaseSchema):
    next_page: HttpUrl | None
    results: list[DetailedPostOutSchema]
