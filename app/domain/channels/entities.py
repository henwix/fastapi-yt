from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.channels.value_objects import Email, Name, Slug
from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class Channel(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    email: Email
    name: Name
    slug: Slug
    description: str = ''
    country: str = ''
    password_hash: str | None
    is_active: bool = True
    avatar_s3_key: str | None = None
    created_at: datetime = field(default_factory=get_current_utc_datetime)
    updated_at: datetime = field(default_factory=get_current_utc_datetime)

    def set_password(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def set_avatar_s3_key(self, key: str | None) -> None:
        self.avatar_s3_key = key

    def set_email(self, email: str) -> None:
        self.email = Email(email)

    def set_slug(self, slug: str) -> None:
        self.slug = Slug(slug)

    @staticmethod
    def create(
        email: str,
        name: str,
        slug: str,
        password_hash: str | None = None,
        description: str = '',
        country: str = '',
        is_active: bool = True,
    ) -> Channel:
        return Channel(
            email=Email(email),
            name=Name(name),
            slug=Slug(slug),
            password_hash=password_hash,
            description=description,
            country=country,
            is_active=is_active,
        )

    def update(
        self,
        name: str | Empty = Empty.UNSET,
        slug: str | Empty = Empty.UNSET,
        description: str | Empty = Empty.UNSET,
        country: str | Empty = Empty.UNSET,
    ) -> None:
        if name is not Empty.UNSET:
            self.name = Name(name)
        if slug is not Empty.UNSET:
            self.slug = Slug(slug)
        if description is not Empty.UNSET:
            self.description = description
        if country is not Empty.UNSET:
            self.country = country
