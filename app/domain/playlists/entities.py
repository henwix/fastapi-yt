from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid7

from app.domain.common.constants import Empty
from app.domain.common.entities import BaseEntity
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum
from app.utils.datetime import get_current_utc_datetime


@dataclass(kw_only=True)
class Playlist(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum
    channel_id: UUID
    created_at: datetime = field(default_factory=get_current_utc_datetime)

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

    def set_title(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.title = value

    def set_description(self, value: str | Empty) -> None:
        if value is not Empty.UNSET:
            self.description = value

    def set_privacy_status(self, value: PlaylistPrivacyStatusEnum | Empty) -> None:
        if value is not Empty.UNSET:
            self.privacy_status = value


@dataclass(kw_only=True)
class PlaylistItem(BaseEntity):
    id: UUID = field(default_factory=uuid7)
    playlist_id: UUID
    video_id: str

    @staticmethod
    def create(playlist_id: UUID, video_id: str) -> PlaylistItem:
        return PlaylistItem(playlist_id=playlist_id, video_id=video_id)
