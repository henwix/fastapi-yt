from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.common.enums import ReactionTypeEnum
from app.domain.video_reactions.entities import VideoReaction
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.infrastructure.sqlalchemy.models.base import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtMixin, UUIDIdMixin
from app.utils.videos import generate_video_id


class VideoORM(CreatedAtMixin, BaseORM):
    __tablename__ = 'videos'

    id: Mapped[str] = mapped_column(
        sa.String(length=11),
        primary_key=True,
        default=generate_video_id,
        unique=True,
    )
    channel_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    title: Mapped[str] = mapped_column(sa.String(length=100))
    description: Mapped[str] = mapped_column(sa.Text)
    privacy_status: Mapped[str] = mapped_column(sa.String(length=10))
    is_reported: Mapped[bool] = mapped_column(default=False, server_default=sa.sql.false())

    upload_id: Mapped[str | None] = mapped_column(default=None, server_default=sa.sql.null(), unique=True)
    s3_key: Mapped[str] = mapped_column(sa.String(length=255), unique=True)
    upload_status: Mapped[str] = mapped_column(sa.String(length=10))

    __table_args__ = (
        sa.Index('ix_videos_composite_channel_id_created_at_id', 'channel_id', 'created_at', 'id'),
        sa.CheckConstraint("id ~ '^[A-Za-z0-9_-]{11}$'"),
        sa.CheckConstraint("privacy_status IN ('public', 'unlisted', 'private')", name='ck_privacy_status'),
        sa.CheckConstraint("upload_status IN ('uploading', 'completed')", name='ck_upload_status'),
        sa.CheckConstraint('char_length(description) <= 5000', name='ck_videos_description_max_length'),
    )

    @staticmethod
    def from_entity(entity: Video) -> VideoORM:
        return VideoORM(
            id=entity.id,
            channel_id=entity.channel_id,
            title=entity.title,
            description=entity.description,
            privacy_status=entity.privacy_status.value,
            is_reported=entity.is_reported,
            upload_id=entity.upload_id,
            s3_key=entity.s3_key,
            upload_status=entity.upload_status.value,
        )

    def to_entity(self) -> Video:
        return Video(
            id=self.id,
            channel_id=self.channel_id,
            title=self.title,
            description=self.description,
            privacy_status=VideoPrivacyStatusEnum(self.privacy_status),
            is_reported=self.is_reported,
            upload_id=self.upload_id,
            s3_key=self.s3_key,
            upload_status=VideoUploadStatusEnum(self.upload_status),
        )


class VideoReactionORM(
    UUIDIdMixin,
    CreatedAtMixin,
    BaseORM,
):
    __tablename__ = 'video_reactions'

    video_id: Mapped[str] = mapped_column(
        sa.ForeignKey('videos.id', ondelete='CASCADE'),
    )
    channel_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    reaction_type: Mapped[str] = mapped_column(sa.String(length=8))

    __table_args__ = (
        sa.UniqueConstraint('video_id', 'channel_id', name='unique_channel_video_reaction'),
        sa.CheckConstraint("reaction_type IN ('positive', 'negative')", name='ck_video_reactions_type'),
    )

    @staticmethod
    def from_entity(entity: VideoReaction) -> VideoReactionORM:
        return VideoReactionORM(
            id=entity.id,
            video_id=entity.video_id,
            channel_id=entity.channel_id,
            reaction_type=entity.reaction_type.value,
            created_at=entity.created_at,
        )

    def to_entity(self) -> VideoReaction:
        return VideoReaction(
            id=self.id,
            video_id=self.video_id,
            channel_id=self.channel_id,
            reaction_type=ReactionTypeEnum(self.reaction_type),
            created_at=self.created_at,
        )
