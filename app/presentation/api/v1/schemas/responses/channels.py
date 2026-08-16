from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, HttpUrl

from app.application.channels.dto import ChannelAboutInfoDTO
from app.domain.channels.entities import Channel
from app.presentation.api.v1.schemas.base import BaseSchema


class ChannelOutSchema(BaseSchema):
    id: UUID
    email: EmailStr
    name: str
    slug: str
    description: str
    country: str
    avatar_s3_key: str | None
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(entity: Channel) -> ChannelOutSchema:
        return ChannelOutSchema(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            country=entity.country,
            avatar_s3_key=entity.avatar_s3_key,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class ChannelAboutInfoOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
    description: str
    country: str
    created_at: datetime
    subscribers_count: int
    videos_count: int
    views_count: int

    @staticmethod
    def from_dto(dto: ChannelAboutInfoDTO) -> ChannelAboutInfoOutSchema:
        return ChannelAboutInfoOutSchema(
            id=dto.id,
            name=dto.name,
            slug=dto.slug,
            description=dto.description,
            country=dto.country,
            created_at=dto.created_at,
            subscribers_count=dto.subscribers_count,
            videos_count=dto.videos_count,
            views_count=dto.views_count,
        )


class GenerateChannelAvatarUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl
    key: str
    channel_id: UUID


class CreateChannelOutSchema(BaseSchema):
    channel: ChannelOutSchema
    activation_required: bool
