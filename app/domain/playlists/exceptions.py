from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions import AppException


@dataclass(kw_only=True)
class PlaylistNotFoundError(AppException):
    message = 'Playlist not found'
    playlist_id: UUID


@dataclass(kw_only=True)
class PlaylistAccessForbiddenError(AppException):
    message = 'Playlist access forbidden'
    playlist_id: UUID
    channel_id: UUID


@dataclass(kw_only=True)
class VideoAlreadyAddedToPlaylistError(AppException):
    message = 'Video already added to playlist'
    playlist_id: UUID
    video_id: str
