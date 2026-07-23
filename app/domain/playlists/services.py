from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from app.domain.channels.entities import Channel
from app.domain.playlists.entities import Playlist, PlaylistItem
from app.domain.playlists.exceptions import PlaylistAccessForbiddenError, PlaylistNotFoundError
from app.domain.playlists.repositories import IPlaylistItemRepository, IPlaylistRepository


class IPlaylistService(ABC):
    @abstractmethod
    async def create(self, playlist: Playlist) -> Playlist: ...

    @abstractmethod
    async def try_update(self, playlist: Playlist) -> Playlist: ...

    @abstractmethod
    async def try_get_by_id(self, id: UUID) -> Playlist: ...

    @abstractmethod
    async def try_delete_by_id(self, id: UUID) -> None: ...

    @abstractmethod
    def ensure_playlist_access(self, playlist: Playlist, channel: Channel) -> None: ...


class IPlaylistItemService(ABC):
    @abstractmethod
    async def create(self, playlist_item: PlaylistItem) -> PlaylistItem: ...


@dataclass
class PlaylistService(IPlaylistService):
    _repo: IPlaylistRepository

    async def create(self, playlist: Playlist) -> Playlist:
        return await self._repo.create(playlist=playlist)

    async def try_update(self, playlist: Playlist) -> Playlist:
        updated_playlist = await self._repo.update(playlist=playlist)
        if updated_playlist is None:
            raise PlaylistNotFoundError(playlist_id=playlist.id)
        return updated_playlist

    async def try_get_by_id(self, id: UUID) -> Playlist:
        playlist = await self._repo.get_by_id(id=id)
        if playlist is None:
            raise PlaylistNotFoundError(playlist_id=id)
        return playlist

    async def try_delete_by_id(self, id: UUID) -> None:
        is_deleted = await self._repo.delete_by_id(id=id)
        if not is_deleted:
            raise PlaylistNotFoundError(playlist_id=id)

    def ensure_playlist_access(self, playlist: Playlist, channel: Channel) -> None:
        if playlist.channel_id != channel.id:
            raise PlaylistAccessForbiddenError(playlist_id=playlist.id, channel_id=channel.id)


@dataclass
class PlaylistItemService(IPlaylistItemService):
    _repo: IPlaylistItemRepository

    async def create(self, playlist_item: PlaylistItem) -> PlaylistItem:
        return await self._repo.create(playlist_item=playlist_item)
