from dataclasses import dataclass
from uuid import UUID

from app.domain.common.constants import Empty
from app.domain.playlists.enums import PlaylistPrivacyStatusEnum


@dataclass(kw_only=True, frozen=True)
class CreatePlaylistCommand:
    current_channel_id: UUID
    title: str
    description: str
    privacy_status: PlaylistPrivacyStatusEnum


@dataclass(kw_only=True, frozen=True)
class UpdatePlaylistCommand:
    current_channel_id: UUID
    playlist_id: UUID
    title: str | Empty = Empty.UNSET
    description: str | Empty = Empty.UNSET
    privacy_status: PlaylistPrivacyStatusEnum | Empty = Empty.UNSET


@dataclass(kw_only=True, frozen=True)
class DeletePlaylistCommand:
    current_channel_id: UUID
    playlist_id: UUID


@dataclass(kw_only=True, frozen=True)
class AddVideoToPlaylistCommand:
    current_channel_id: UUID
    playlist_id: UUID
    video_id: str
