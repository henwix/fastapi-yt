from datetime import datetime
from uuid import UUID

from app.domain.posts.entities import Post
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreatePostSchema(BaseSchema):
    text: str


class UpdatePostSchema(BaseUpdateSchema):
    text: str = ''


class GetPostSchema(BaseSchema):
    id: UUID
    text: str
    created_at: datetime

    @staticmethod
    def from_entity(entity: Post) -> GetPostSchema:
        return GetPostSchema(
            id=entity.id,
            text=entity.text,
            created_at=entity.created_at,
        )
