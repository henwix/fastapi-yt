from uuid import UUID

import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.common.enums import ReactionTypeEnum
from app.domain.playlists.entities import Playlist, PlaylistItem
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.domain.video_comments.entities import VideoComment
from app.domain.video_history.entities import VideoHistoryItem
from app.domain.video_reactions.entities import VideoReaction
from app.domain.video_views.entities import VideoView
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.infrastructure.sqlalchemy.models.base import BaseORM
from app.infrastructure.sqlalchemy.models.mixins import CreatedAtDateMixin, CreatedAtDatetimeMixin, UUIDIdMixin
from app.utils.videos import generate_video_id


class VideoORM(CreatedAtDatetimeMixin, BaseORM):
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
    views_count: Mapped[int] = mapped_column(
        default=0,
        server_default='0',
    )

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
            views_count=entity.views_count,
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
            views_count=self.views_count,
            upload_id=self.upload_id,
            s3_key=self.s3_key,
            upload_status=VideoUploadStatusEnum(self.upload_status),
        )


class VideoReactionORM(
    UUIDIdMixin,
    CreatedAtDatetimeMixin,
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


class VideoViewORM(UUIDIdMixin, CreatedAtDateMixin, BaseORM):
    __tablename__ = 'video_views'

    video_id: Mapped[str] = mapped_column(sa.ForeignKey('videos.id', ondelete='CASCADE'))
    channel_id: Mapped[UUID | None] = mapped_column(sa.ForeignKey('channels.id', ondelete='CASCADE'))
    anonymous_id: Mapped[UUID | None]
    views_count: Mapped[int] = mapped_column(
        default=1,
        server_default='1',
    )

    __table_args__ = (
        sa.Index(
            'unique_video_views_channel_view',
            'video_id',
            'channel_id',
            'created_at',
            unique=True,
            postgresql_where=sa.text('channel_id IS NOT NULL'),
        ),
        sa.Index(
            'unique_video_views_anonymous_view',
            'video_id',
            'anonymous_id',
            'created_at',
            unique=True,
            postgresql_where=sa.text('anonymous_id IS NOT NULL'),
        ),
    )

    @staticmethod
    def from_entity(entity: VideoView) -> VideoViewORM:
        return VideoViewORM(
            id=entity.id,
            video_id=entity.video_id,
            channel_id=entity.channel_id,
            anonymous_id=entity.anonymous_id,
            views_count=entity.views_count,
            created_at=entity.created_at,
        )

    def to_entity(self) -> VideoView:
        return VideoView(
            id=self.id,
            video_id=self.video_id,
            channel_id=self.channel_id,
            anonymous_id=self.anonymous_id,
            views_count=self.views_count,
            created_at=self.created_at,
        )


class PlaylistORM(UUIDIdMixin, CreatedAtDatetimeMixin, BaseORM):
    __tablename__ = 'playlists'

    title: Mapped[str] = mapped_column(sa.String(length=150))
    description: Mapped[str] = mapped_column(sa.Text)
    privacy_status: Mapped[str] = mapped_column(sa.String(length=10))
    channel_id: Mapped[UUID] = mapped_column(sa.ForeignKey('channels.id', ondelete='CASCADE'))

    __table_args__ = (
        sa.CheckConstraint("privacy_status IN ('public', 'unlisted', 'private')", name='ck_playlists_privacy_status'),
        sa.CheckConstraint('char_length(description) <= 5000', name='ck_playlists_description_max_length'),
        sa.Index('ix_playlists_composite_channel_id_created_at_id', 'channel_id', 'created_at', 'id'),
    )

    @staticmethod
    def from_entity(entity: Playlist) -> PlaylistORM:
        return PlaylistORM(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            privacy_status=entity.privacy_status.value,
            channel_id=entity.channel_id,
            created_at=entity.created_at,
        )

    def to_entity(self) -> Playlist:
        return Playlist(
            id=self.id,
            title=self.title,
            description=self.description,
            privacy_status=PlaylistPrivacyStatusEnum(self.privacy_status),
            channel_id=self.channel_id,
            created_at=self.created_at,
        )


class PlaylistItemORM(UUIDIdMixin, CreatedAtDatetimeMixin, BaseORM):
    __tablename__ = 'playlist_items'

    playlist_id: Mapped[UUID] = mapped_column(sa.ForeignKey('playlists.id', ondelete='CASCADE'))
    video_id: Mapped[str] = mapped_column(sa.ForeignKey('videos.id', ondelete='CASCADE'))

    __table_args__ = (
        sa.UniqueConstraint('playlist_id', 'video_id', name='unique_playlist_item'),
        sa.Index('ix_playlist_items_composite_added_at_filter', 'playlist_id', 'created_at', 'video_id'),
    )

    @staticmethod
    def from_entity(entity: PlaylistItem) -> PlaylistItemORM:
        return PlaylistItemORM(
            id=entity.id,
            playlist_id=entity.playlist_id,
            video_id=entity.video_id,
        )

    def to_entity(self) -> PlaylistItem:
        return PlaylistItem(
            id=self.id,
            playlist_id=self.playlist_id,
            video_id=self.video_id,
        )


class VideoHistoryItemORM(CreatedAtDatetimeMixin, UUIDIdMixin, BaseORM):
    __tablename__ = 'video_history_items'

    channel_id: Mapped[UUID] = mapped_column(sa.ForeignKey('channels.id', ondelete='CASCADE'))
    video_id: Mapped[str] = mapped_column(sa.ForeignKey('videos.id', ondelete='CASCADE'))

    __table_args__ = (
        sa.UniqueConstraint('channel_id', 'video_id', name='unique_video_history_item'),
        sa.Index('ix_video_history_items_composite_added_at_filter', 'channel_id', 'created_at', 'video_id'),
    )

    @staticmethod
    def from_entity(entity: VideoHistoryItem) -> VideoHistoryItemORM:
        return VideoHistoryItemORM(
            id=entity.id,
            channel_id=entity.channel_id,
            video_id=entity.video_id,
            created_at=entity.created_at,
        )

    def to_entity(self) -> VideoHistoryItem:
        return VideoHistoryItem(
            id=self.id,
            channel_id=self.channel_id,
            video_id=self.video_id,
            created_at=self.created_at,
        )


class VideoCommentORM(
    UUIDIdMixin,
    CreatedAtDatetimeMixin,
    BaseORM,
):
    __tablename__ = 'video_comments'

    video_id: Mapped[str] = mapped_column(
        sa.ForeignKey('videos.id', ondelete='CASCADE'),
    )
    channel_id: Mapped[UUID] = mapped_column(
        sa.ForeignKey('channels.id', ondelete='CASCADE'),
    )
    reply_comment_id: Mapped[UUID | None] = mapped_column(
        sa.ForeignKey('video_comments.id'),
        default=None,
        server_default=sa.sql.null(),
    )
    is_edited: Mapped[bool] = mapped_column(
        default=False,
        server_default=sa.sql.false(),
    )
    text: Mapped[str] = mapped_column(sa.Text)
    reply_level: Mapped[int] = mapped_column(default=0, server_default=sa.text('0'))

    __table_args__ = (
        sa.CheckConstraint('reply_level IN (0, 1)', name='ck_video_comments_reply_level'),
        sa.CheckConstraint('char_length(text) <= 10000', name='ck_video_comments_text_max_length'),
        sa.Index(
            'ix_video_comments_composite_comments',
            'video_id',
            'reply_level',
            'created_at',
            'id',
        ),
        sa.Index(
            'ix_video_comments_composite_replies',
            'reply_comment_id',
            'reply_level',
            'created_at',
            'id',
        ),
    )

    @staticmethod
    def from_entity(entity: VideoComment) -> VideoCommentORM:
        return VideoCommentORM(
            id=entity.id,
            video_id=entity.video_id,
            channel_id=entity.channel_id,
            reply_comment_id=entity.reply_comment_id,
            is_edited=entity.is_edited,
            text=entity.text,
            reply_level=entity.reply_level,
            created_at=entity.created_at,
        )

    def to_entity(self) -> VideoComment:
        return VideoComment(
            id=self.id,
            video_id=self.video_id,
            channel_id=self.channel_id,
            reply_comment_id=self.reply_comment_id,
            is_edited=self.is_edited,
            text=self.text,
            reply_level=self.reply_level,
            created_at=self.created_at,
        )
