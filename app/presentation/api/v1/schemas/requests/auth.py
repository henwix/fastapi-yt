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
from app.presentation.api.v1.schemas.base import BaseSchema


class RegisterChannelWithPasswordInSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr = Field(max_length=CHANNEL_EMAIL_MAX_LENGTH)
    name: str = Field(min_length=CHANNEL_NAME_MIN_LENGTH, max_length=CHANNEL_NAME_MAX_LENGTH)
    slug: str = Field(min_length=CHANNEL_SLUG_MIN_LENGTH, max_length=CHANNEL_SLUG_MAX_LENGTH, pattern=SLUG_PATTERN)
    description: str = Field(default='', max_length=CHANNEL_DESCRIPTION_MAX_LENGTH)
    country: str = Field(default='', max_length=CHANNEL_COUNTRY_MAX_LENGTH)
    password: str

    @field_validator('name', 'slug', 'description', 'country', mode='before')
    @classmethod
    def strip_whitespace_validator(cls, v: str) -> str:
        return v.strip()


class RegisterChannelWithEmailInSchema(BaseSchema):
    email: EmailStr = Field(max_length=CHANNEL_EMAIL_MAX_LENGTH)
    name: str = Field(min_length=CHANNEL_NAME_MIN_LENGTH, max_length=CHANNEL_NAME_MAX_LENGTH)
    slug: str = Field(min_length=CHANNEL_SLUG_MIN_LENGTH, max_length=CHANNEL_SLUG_MAX_LENGTH, pattern=SLUG_PATTERN)
    description: str = Field(default='', max_length=CHANNEL_DESCRIPTION_MAX_LENGTH)
    country: str = Field(default='', max_length=CHANNEL_COUNTRY_MAX_LENGTH)


class LoginWithPasswordInSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr
    password: str


class LoginWithEmailCodeInSchema(BaseSchema):
    email: EmailStr


class LoginWithEmailCodeConfirmInSchema(BaseSchema):
    code: str = Field(min_length=32, max_length=32)
    uid: str = Field(min_length=51, max_length=51)


class RefreshJWTTokenInSchema(BaseSchema):
    refresh: str


class LogoutInSchema(BaseSchema):
    refresh: str


class ActivateChannelInSchema(BaseSchema):
    code: str = Field(min_length=32, max_length=32)


class SetChannelEmailInSchema(BaseSchema):
    new_email: EmailStr


class SetChannelEmailConfirmInSchema(BaseSchema):
    code: str = Field(min_length=32, max_length=32)


class SetChannelPasswordInSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    new_password: str


class ResetChannelPasswordInSchema(BaseSchema):
    email: EmailStr


class ResetChannelPasswordConfirmInSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    code: str = Field(min_length=32, max_length=32)
    uid: str = Field(min_length=51, max_length=51)
    new_password: str

    @field_validator('code', 'uid', mode='before')
    @classmethod
    def strip_whitespace_validator(cls, v: str) -> str:
        return v.strip()
