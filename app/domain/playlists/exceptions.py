from dataclasses import dataclass
from uuid import UUID

from app.domain.common.exceptions.base import AppError


@dataclass(kw_only=True)
class PlaylistNotFoundError(AppError):
    message = 'Playlist not found'
    playlist_id: UUID


@dataclass(kw_only=True)
class PlaylistAccessForbiddenError(AppError):
    message = 'Playlist access forbidden'
    playlist_id: UUID
    channel_id: UUID | None


@dataclass(kw_only=True)
class VideoAlreadyAddedToPlaylistError(AppError):
    message = 'Video already added to playlist'
    playlist_id: UUID
    video_id: str


@dataclass(kw_only=True)
class VideoNotFoundInPlaylistError(AppError):
    message = 'Video not found in playlist'
    playlist_id: UUID
    video_id: str
