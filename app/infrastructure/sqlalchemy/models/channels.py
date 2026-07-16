from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.channels.entities import Channel
from app.domain.subscriptions.entities import Subscription
from app.infrastructure.sqlalchemy.models.base import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtMixin, UpdatedAtMixin, UUIDIdMixin


class ChannelORM(
    UUIDIdMixin,
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
    avatar_s3_key: Mapped[str] = mapped_column(
        sa.String(length=255), nullable=True, default=None, server_default=sa.sql.null()
    )

    subscriptions = relationship(
        'SubscriptionORM',
        back_populates='subscriber',
        foreign_keys='SubscriptionORM.subscriber_id',
    )
    subscribers = relationship(
        'SubscriptionORM',
        back_populates='subscribed_to',
        foreign_keys='SubscriptionORM.subscribed_to_id',
    )

    __table_args__ = (
        sa.CheckConstraint('char_length(description) <= 1000', name='ck_channels_description_max_length'),
    )

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
            avatar_s3_key=self.avatar_s3_key,
            created_at=self.created_at,
            updated_at=self.updated_at,
        )

    @staticmethod
    def from_entity(entity: Channel) -> ChannelORM:
        return ChannelORM(
            id=entity.id,
            email=entity.email,
            name=entity.name,
            slug=entity.slug,
            description=entity.description,
            country=entity.country,
            password_hash=entity.password_hash,
            is_active=entity.is_active,
            avatar_s3_key=entity.avatar_s3_key,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )


class SubscriptionORM(
    UUIDIdMixin,
    CreatedAtMixin,
    BaseORM,
):
    __tablename__ = 'subscriptions'

    subscriber_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    subscriber = relationship(
        'ChannelORM',
        back_populates='subscriptions',
        foreign_keys=[subscriber_id],
    )
    subscribed_to_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    subscribed_to = relationship(
        'ChannelORM',
        back_populates='subscribers',
        foreign_keys=[subscribed_to_id],
    )

    __table_args__ = (
        sa.UniqueConstraint('subscriber_id', 'subscribed_to_id', name='unique_channel_subscription'),
        sa.Index('ix_composite_subscriber_id_created_at_id', 'subscriber_id', 'created_at', 'id'),
        sa.Index('ix_composite_subscribed_to_id_created_at_id', 'subscribed_to_id', 'created_at', 'id'),
    )

    def to_entity(self) -> Subscription:
        return Subscription(
            id=self.id,
            subscriber_id=self.subscriber_id,
            subscribed_to_id=self.subscribed_to_id,
            created_at=self.created_at,
        )

    @staticmethod
    def from_entity(entity: Subscription) -> SubscriptionORM:
        return SubscriptionORM(
            id=entity.id,
            subscriber_id=entity.subscriber_id,
            subscribed_to_id=entity.subscribed_to_id,
            created_at=entity.created_at,
        )
