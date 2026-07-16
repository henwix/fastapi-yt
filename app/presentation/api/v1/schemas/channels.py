import re
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, HttpUrl, field_validator

from app.domain.channels.constants import (
    CHANNEL_COUNTRY_MAX_LENGTH,
    CHANNEL_DESCRIPTION_MAX_LENGTH,
    CHANNEL_EMAIL_MAX_LENGTH,
    CHANNEL_NAME_MAX_LENGTH,
    CHANNEL_NAME_MIN_LENGTH,
    CHANNEL_SLUG_MAX_LENGTH,
    CHANNEL_SLUG_MIN_LENGTH,
)
from app.domain.channels.entities import Channel
from app.domain.common.constants import FILENAME_MAX_LENGTH, FILENAME_PATTERN, SLUG_PATTERN
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


class CreateChannelInSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr = Field(max_length=CHANNEL_EMAIL_MAX_LENGTH)
    name: str = Field(min_length=CHANNEL_NAME_MIN_LENGTH, max_length=CHANNEL_NAME_MAX_LENGTH)
    slug: str = Field(min_length=CHANNEL_SLUG_MIN_LENGTH, max_length=CHANNEL_SLUG_MAX_LENGTH)
    description: str = Field(default='', max_length=CHANNEL_DESCRIPTION_MAX_LENGTH)
    country: str = Field(default='', max_length=CHANNEL_COUNTRY_MAX_LENGTH)
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


class UpdateChannelInSchema(BaseUpdateSchema):
    name: str = Field(default='', min_length=CHANNEL_NAME_MIN_LENGTH, max_length=CHANNEL_NAME_MAX_LENGTH)
    slug: str = Field(default='', min_length=CHANNEL_SLUG_MIN_LENGTH, max_length=CHANNEL_SLUG_MAX_LENGTH)
    description: str = Field(default='', max_length=CHANNEL_DESCRIPTION_MAX_LENGTH)
    country: str = Field(default='', max_length=CHANNEL_COUNTRY_MAX_LENGTH)

    @field_validator('slug', mode='after')
    @classmethod
    def slug_regex_validator(cls, v: str) -> str:
        if v and not re.fullmatch(pattern=SLUG_PATTERN, string=v):
            raise ValueError(f"String should match pattern '{SLUG_PATTERN}'")
        return v


class SetChannelPasswordInSchema(BaseModel):
    new_password: str


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


class GenerateChannelAvatarUploadUrlInSchema(BaseSchema):
    filename: str = Field(max_length=FILENAME_MAX_LENGTH, pattern=FILENAME_PATTERN, examples=['avatar_image.png'])


class GenerateChannelAvatarUploadUrlOutSchema(BaseSchema):
    upload_url: HttpUrl
    key: str
    channel_id: UUID


class ChannelAvatarUploadConfirmInSchema(BaseSchema):
    key: str
