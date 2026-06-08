from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.common.enums import ReactionTypeEnum
from app.domain.post_reactions.entities import PostReaction
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


class PostReactionORM(
    UUIDIdMixin,
    CreatedAtMixin,
    BaseORM,
):
    __tablename__ = 'post_reactions'

    post_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('posts.id', ondelete='CASCADE'),
    )
    channel_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    reaction_type: Mapped[str] = mapped_column(
        sa.Enum(
            ReactionTypeEnum,
            values_callable=lambda x: [e.value for e in x],
            name='reaction_type',
        ),
    )

    __table_args__ = (
        sa.UniqueConstraint(
            'post_id',
            'channel_id',
            name='unique_channel_post_reaction',
        ),
    )

    def to_entity(self) -> PostReaction:
        return PostReaction(
            id=self.id,
            post_id=self.post_id,
            channel_id=self.channel_id,
            reaction_type=self.reaction_type,
            created_at=self.created_at,
        )

    @staticmethod
    def from_entity(entity: PostReaction) -> PostReactionORM:
        return PostReactionORM(
            id=entity.id,
            post_id=entity.post_id,
            channel_id=entity.channel_id,
            reaction_type=entity.reaction_type,
            created_at=entity.created_at,
        )
