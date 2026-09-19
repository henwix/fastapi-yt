from fastapi import status

from app.domain.common.exceptions.base import AppError
from app.domain.playlists.exceptions import (
    PlaylistAccessForbiddenError,
    PlaylistNotFoundError,
    VideoAlreadyAddedToPlaylistError,
    VideoNotFoundInPlaylistError,
)


def init_playlists() -> dict[type[AppError], int]:
    return {
        VideoAlreadyAddedToPlaylistError: status.HTTP_409_CONFLICT,
        PlaylistAccessForbiddenError: status.HTTP_403_FORBIDDEN,
        PlaylistNotFoundError: status.HTTP_404_NOT_FOUND,
        VideoNotFoundInPlaylistError: status.HTTP_404_NOT_FOUND,
    }
