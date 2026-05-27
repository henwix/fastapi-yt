import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.channels.entities import Channel
from app.infrastructure.sqlalchemy.models.base import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtMixin, IntIDMixin, UpdatedAtMixin


class ChannelORM(
    IntIDMixin,
    CreatedAtMixin,
    UpdatedAtMixin,
    BaseORM,
):
    __tablename__ = 'channels'

    email: Mapped[str] = mapped_column(sa.String(255), unique=True)
    name: Mapped[str] = mapped_column(sa.String(100))
    slug: Mapped[str] = mapped_column(sa.String(40), unique=True)
    description: Mapped[str] = mapped_column(sa.Text)
    country: Mapped[str] = mapped_column(sa.String(40))
    password_hash: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True, server_default=sa.sql.true())

    def to_entity(self) -> Channel:
        return Channel(
            id=self.id,
            email=self.email,
            name=self.name,
            slug=self.slug,
            description=self.description,
            country=self.country,
            password_hash=self.password_hash,
            is_active=self.is_active,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(entity: Channel) -> ChannelORM:
        return ChannelORM(
            email=entity.email,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            country=entity.country,
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )
