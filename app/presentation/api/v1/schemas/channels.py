import re
from datetime import datetime
from typing import Self

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.domain.channels.entities import Channel
from app.presentation.api.v1.schemas.base import BaseSchema

slug_pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'


class CreateChannelSchema(BaseModel):
    model_config = ConfigDict(extra='forbid')

    email: EmailStr = Field(max_length=255)
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=40)
    description: str = Field(default='')
    country: str = Field(default='')
    password: str

    @field_validator('name', 'slug', 'description', 'country', mode='before')
    @classmethod
    def strip_whitespace_validator(cls, v: str) -> str:
        return v.strip()

    @field_validator('slug', mode='after')
    @classmethod
    def slug_regex_validator(cls, v: str) -> str:
        if not re.fullmatch(pattern=slug_pattern, string=v):
            raise ValueError(f"String should match pattern '{slug_pattern}'")
        return v


class UpdateChannelSchema(BaseSchema):
    name: str = Field(default='', min_length=1, max_length=100)
    slug: str = Field(default='', min_length=1, max_length=40)
    description: str = Field(default='')
    country: str = Field(default='')

    @field_validator('slug', mode='after')
    @classmethod
    def slug_regex_validator(cls, v: str) -> str:
        if v and not re.fullmatch(pattern=slug_pattern, string=v):
            raise ValueError(f"String should match pattern '{slug_pattern}'")
        return v

    @model_validator(mode='after')
    def empty_schema_validator(self) -> Self:
        if not self.model_fields_set:
            raise ValueError('At least one field must be provided')
        return self


class SetChannelPasswordSchema(BaseModel):
    new_password: str


class GetChannelSchema(BaseSchema):
    email: EmailStr
    name: str
    slug: str
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
