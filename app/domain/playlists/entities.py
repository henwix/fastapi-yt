from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.utils.get_datetime_utc_now import get_datetime_utc_now


@dataclass(kw_only=True)
class Playlist(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum
    channel_id: UUID
    created_at: datetime = field(default_factory=get_datetime_utc_now)

    @staticmethod
    def create(
        title: str,
        description: str,
        privacy_status: PlaylistPrivacyStatusEnum,
        channel_id: UUID,
    ) -> Playlist:
        return Playlist(
            title=title,
            description=description,
            privacy_status=privacy_status,
            channel_id=channel_id,
        )

    def update(
        self,
        title: str | Empty,
        description: str | Empty,
        privacy_status: PlaylistPrivacyStatusEnum | Empty,
    ):
        if title is not Empty.UNSET:
            self.title = title
        if description is not Empty.UNSET:
            self.description = description
        if privacy_status is not Empty.UNSET:
            self.privacy_status = privacy_status


@dataclass(kw_only=True)
class PlaylistItem(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    playlist_id: UUID
    video_id: str

    @staticmethod
    def create(playlist_id: UUID, video_id: str) -> PlaylistItem:
        return PlaylistItem(playlist_id=playlist_id, video_id=video_id)
