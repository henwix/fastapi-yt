from dataclasses import dataclass, field
from datetime import datetime

from app.domain.common.entities import BaseEntity
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class Channel(BaseEntity):
    id: int | None = None
    email: str
    name: str
    slug: str
    description: str = ''
    country: str = ''
    password_hash: str
    is_active: bool = True
    created_at: datetime = field(default_factory=get_datetime_utc_now)
    updated_at: datetime = field(default_factory=get_datetime_utc_now)

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
