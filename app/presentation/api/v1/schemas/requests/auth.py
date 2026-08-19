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
from app.domain.common.constants import SLUG_PATTERN


class RegisterChannelInSchema(BaseModel):
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


class LoginInSchema(BaseModel):
    email: EmailStr
    password: str


class ActivateChannelInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)


class SetChannelEmailInSchema(BaseModel):
    new_email: EmailStr


class SetChannelEmailConfirmInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)


class SetChannelPasswordInSchema(BaseModel):
    new_password: str


class ResetChannelPasswordInSchema(BaseModel):
    email: EmailStr


class ResetChannelPasswordConfirmInSchema(BaseModel):
    code: str = Field(min_length=32, max_length=32)
    uid: str = Field(min_length=51, max_length=51)
    new_password: str
