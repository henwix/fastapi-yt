from dataclasses import dataclass, field
from datetime import datetime

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class Channel(BaseEntity):
    email: str
    name: str
    slug: str
    description: str = ''
    country: str = ''
    password_hash: str
    is_active: bool = True
    avatar_s3_key: str | None = None
    created_at: datetime = field(default_factory=get_datetime_utc_now)
    updated_at: datetime = field(default_factory=get_datetime_utc_now)

    def set_password(self, password_hash: str) -> None:
        self.password_hash = password_hash

    def set_avatar_s3_key(self, key: str | None) -> None:
        self.avatar_s3_key = key

    @staticmethod
    def create(
        email: str,
        name: str,
        slug: str,
        password_hash: str,
        description: str = '',
        country: str = '',
    ) -> Channel:
        return Channel(
            email=email,
            name=name,
            slug=slug,
            password_hash=password_hash,
            description=description,
            country=country,
        )

    def update(
        self,
        name: str | Empty = Empty.UNSET,
        slug: str | Empty = Empty.UNSET,
        description: str | Empty = Empty.UNSET,
        country: str | Empty = Empty.UNSET,
    ) -> None:
        if name is not Empty.UNSET:
            self.name = name
        if slug is not Empty.UNSET:
            self.slug = slug
        if description is not Empty.UNSET:
            self.description = description
        if country is not Empty.UNSET:
            self.country = country
