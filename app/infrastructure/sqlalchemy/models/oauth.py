from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.oauth.entities import OAuthAccount
from app.domain.oauth.enums import OAuthProviderEnum
from app.infrastructure.sqlalchemy.models.base import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtDatetimeMixin, UUIDIdMixin


class OAuthAccountORM(CreatedAtDatetimeMixin, UUIDIdMixin, BaseORM):
    __tablename__ = 'oauth_accounts'

    channel_id: Mapped[UUID] = mapped_column(sa.ForeignKey('channels.id', ondelete='CASCADE'))
    provider_uid: Mapped[str]
    provider: Mapped[str] = mapped_column(sa.String(length=32))

    __table_args__ = (
        sa.UniqueConstraint('channel_id', 'provider', name='uq_channel_provider'),
        sa.UniqueConstraint('provider_uid', 'provider', name='uq_provider_uid'),
        sa.CheckConstraint("provider IN ('google', 'github')", 'ck_provider'),
    )

    @staticmethod
    def from_entity(entity: OAuthAccount) -> OAuthAccountORM:
        return OAuthAccountORM(
            id=entity.id,
            channel_id=entity.channel_id,
            provider_uid=entity.provider_uid,
            provider=entity.provider.value,
            created_at=entity.created_at,
        )

    def to_entity(self) -> OAuthAccount:
        return OAuthAccount(
            id=self.id,
            channel_id=self.channel_id,
            provider_uid=self.provider_uid,
            provider=OAuthProviderEnum(self.provider),
            created_at=self.created_at,
        )
