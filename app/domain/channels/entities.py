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

    def set_email(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.email = Email(value)

    def set_name(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.name = Name(value)

    def set_slug(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.slug = Slug(value)

    def set_description(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.description = value

    def set_country(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.country = value

    def set_avatar_s3_key(self, value: str | None | Empty) -> None:
        if value is not Empty.UNSET:
            self.avatar_s3_key = value
