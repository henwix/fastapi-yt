from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.application.common.pagination import CursorPagination
from app.application.playlists.dto import DetailedPlaylistDTO, PlaylistPreviewVideoDTO, PreviewPlaylistDTO
from app.application.playlists.queries import PlaylistsPreviewSorting, PlaylistVideosSorting


class IPlaylistReader(ABC):
    @abstractmethod
    async def try_get_detailed_playlist_by_id(self, id: UUID) -> DetailedPlaylistDTO: ...

    @abstractmethod
    async def get_playlists_by_channel_id(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PlaylistsPreviewSorting,
        pagination: CursorPagination,
    ) -> list[PreviewPlaylistDTO]: ...

    @abstractmethod
    async def get_public_playlists_by_channel_id(
        self,
        channel_id: UUID,
        cursor_sort_value: datetime | None,
        cursor_id_value: UUID | None,
        sorting: PlaylistsPreviewSorting,
        pagination: CursorPagination,
    ) -> list[PreviewPlaylistDTO]: ...

    @abstractmethod
    async def get_playlist_videos_by_playlist_id(
        self,
        playlist_id: UUID,
        cursor_sort_value: datetime | int | None,
        cursor_id_value: str | None,
        sorting: PlaylistVideosSorting,
        pagination: CursorPagination,
    ) -> list[PlaylistPreviewVideoDTO]: ...
