from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.posts.entities import Post
from app.infrastructure.sqlalchemy.models.base import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtMixin, UUIDIdMixin


class PostORM(
    UUIDIdMixin,
    CreatedAtMixin,
    BaseORM,
):
    __tablename__ = 'posts'

    channel_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
        index=True,
    )
    text: Mapped[str] = mapped_column(sa.Text)

    @staticmethod
    def from_entity(entity: Post) -> PostORM:
        return PostORM(
            id=entity.id,
            channel_id=entity.channel_id,
            text=entity.text,
            created_at=entity.created_at,
        )

    def to_entity(self) -> Post:
        return Post(
            id=self.id,
            channel_id=self.channel_id,
            text=self.text,
            created_at=self.created_at,
        )


class PostReactionORM(UUIDIdMixin, BaseORM):
    __tablename__ = 'post_reactions'

    post_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('posts.id', ondelete='CASCADE'),
    )
    channel_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    is_positive: Mapped[bool] = mapped_column(
        default=True,
        server_default=sa.sql.true(),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'post_id',
            'channel_id',
            name='unique_channel_post_reaction',
        ),
    )
