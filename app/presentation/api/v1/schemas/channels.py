from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.domain.channels.entities import Channel


class BaseChannelSchema(BaseModel):
    email: EmailStr = Field(max_length=255)
    name: str = Field(max_length=100)
    slug: str = Field(max_length=40)


class CreateChannelSchema(BaseChannelSchema):
    description: str = Field(default='')
    country: str = Field(default='')
    password: str


class GetChannelSchema(BaseChannelSchema):
    description: str
    country: str
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def from_entity(entity: Channel) -> GetChannelSchema:
        return GetChannelSchema(
            email=entity.email,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            country=entity.country,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
