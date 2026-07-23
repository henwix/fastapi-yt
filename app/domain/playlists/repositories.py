from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.playlists.entities import Playlist, PlaylistItem


class IPlaylistRepository(ABC):
    @abstractmethod
    async def create(self, playlist: Playlist) -> Playlist: ...

    @abstractmethod
    async def update(self, playlist: Playlist) -> Playlist | None: ...

    @abstractmethod
    async def get_by_id(self, id: UUID) -> Playlist | None: ...

    @abstractmethod
    async def delete_by_id(self, id: UUID) -> bool: ...


class IPlaylistItemRepository(ABC):
    @abstractmethod
    async def create(self, playlist_item: PlaylistItem) -> PlaylistItem: ...
