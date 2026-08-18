import re

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.domain.channels.constants import (
    CHANNEL_COUNTRY_MAX_LENGTH,
    CHANNEL_DESCRIPTION_MAX_LENGTH,
    CHANNEL_EMAIL_MAX_LENGTH,
    CHANNEL_NAME_MAX_LENGTH,
    CHANNEL_NAME_MIN_LENGTH,
    CHANNEL_SLUG_MAX_LENGTH,
    CHANNEL_SLUG_MIN_LENGTH,
)
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


class GenerateChannelAvatarUploadUrlInSchema(BaseSchema):
    filename: str = Field(max_length=FILENAME_MAX_LENGTH, pattern=FILENAME_PATTERN, examples=['avatar_image.png'])


class ChannelAvatarUploadConfirmInSchema(BaseSchema):
    key: str
