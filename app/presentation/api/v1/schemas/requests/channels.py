import re

from pydantic import Field, field_validator

from app.domain.channels.constants import (
    CHANNEL_COUNTRY_MAX_LENGTH,
    CHANNEL_DESCRIPTION_MAX_LENGTH,
    CHANNEL_NAME_MAX_LENGTH,
    CHANNEL_NAME_MIN_LENGTH,
    CHANNEL_SLUG_MAX_LENGTH,
    CHANNEL_SLUG_MIN_LENGTH,
)
from app.domain.common.constants import FILENAME_MAX_LENGTH, FILENAME_PATTERN, SLUG_PATTERN
from app.presentation.api.v1.schemas.base import BaseSchema, BaseUpdateSchema


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
