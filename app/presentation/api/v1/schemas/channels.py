import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from app.domain.channels.entities import Channel
from app.domain.common.constants import FILENAME_PATTERN, SLUG_PATTERN
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreateChannelSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr = Field(max_length=255)
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=40)
    description: str = ''
    country: str = ''
    password: str

    @field_validator('name', 'slug', 'description', 'country', mode='before')
    @classmethod
    def strip_whitespace_validator(cls, v: str) -> str:
        return v.strip()

    @field_validator('slug', mode='after')
    @classmethod
    def slug_regex_validator(cls, v: str) -> str:
        if not re.fullmatch(pattern=SLUG_PATTERN, string=v):
            raise ValueError(f"String should match pattern '{SLUG_PATTERN}'")
        return v


class UpdateChannelSchema(BaseUpdateSchema):
    name: str = Field(default='', min_length=1, max_length=100)
    slug: str = Field(default='', min_length=1, max_length=40)
    description: str = ''
    country: str = ''

    @field_validator('slug', mode='after')
    @classmethod
    def slug_regex_validator(cls, v: str) -> str:
        if v and not re.fullmatch(pattern=SLUG_PATTERN, string=v):
            raise ValueError(f"String should match pattern '{SLUG_PATTERN}'")
        return v


class SetChannelPasswordSchema(BaseModel):
    new_password: str


class ChannelSchema(BaseSchema):
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
    def from_entity(entity: Channel) -> ChannelSchema:
        return ChannelSchema(
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


class GenerateChannelAvatarUploadURLInSchema(BaseSchema):
    filename: str = Field(max_length=100, pattern=FILENAME_PATTERN, examples=['avatar_image.png'])


class GenerateChannelAvatarUploadURLOutSchema(BaseSchema):
    upload_url: HttpUrl
    key: str
    channel_id: UUID


class ChannelAvatarUploadConfirmSchema(BaseSchema):
    key: str
