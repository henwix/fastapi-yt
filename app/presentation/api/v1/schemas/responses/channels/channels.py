from datetime import datetime
from uuid import UUID

from pydantic import EmailStr, HttpUrl

from app.application.channels.dto import ChannelAboutInfo, DetailedChannel
from app.domain.channels.entities import Channel
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.presentation.api.v1.schemas.base import BaseSchema


class ChannelOutSchema(BaseSchema):
    id: UUID
    name: str
    email: EmailStr
    slug: str
    description: str
    country: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deletion_status: ChannelDeletionStatusEnum
    deleted_at: datetime | None

    @staticmethod
    def from_entity(entity: Channel) -> ChannelOutSchema:
        return ChannelOutSchema(
            id=entity.id,
            name=entity.name.to_raw(),
            email=entity.email.to_raw(),
            slug=entity.slug.to_raw(),
            description=entity.description,
            country=entity.country,
            created_at=entity.created_at,
            is_active=entity.is_active,
            deletion_status=entity.deletion_status,
            deleted_at=entity.deleted_at.to_raw(),
            updated_at=entity.updated_at,
        )


class DetailedChannelOutSchema(BaseSchema):
    id: UUID
    name: str
    email: EmailStr
    slug: str
    description: str
    country: str
    created_at: datetime
    updated_at: datetime
    is_active: bool
    deletion_status: ChannelDeletionStatusEnum
    deleted_at: datetime | None
    avatar_url: HttpUrl | None

    @staticmethod
    def from_dto(dto: DetailedChannel) -> DetailedChannelOutSchema:
        return DetailedChannelOutSchema(
            id=dto.id,
            name=dto.name,
            email=dto.email,
            slug=dto.slug,
            description=dto.description,
            country=dto.country,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
            is_active=dto.is_active,
            deletion_status=dto.deletion_status,
            deleted_at=dto.deleted_at,
            avatar_url=dto.avatar_url,
        )


class UpdateChannelOutSchema(BaseSchema):
    id: UUID
    name: str
    slug: str
    description: str
    country: str

    @staticmethod
    def from_entity(entity: Channel) -> UpdateChannelOutSchema:
        return UpdateChannelOutSchema(
            id=entity.id,
            name=entity.name.to_raw(),
            slug=entity.slug.to_raw(),
            description=entity.description,
            country=entity.country,
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
    def from_dto(dto: ChannelAboutInfo) -> ChannelAboutInfoOutSchema:
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
