from typing import NoReturn
from uuid import UUID

from sqlalchemy import delete, select, update
from sqlalchemy.exc import DBAPIError, IntegrityError

from app.domain.channels.exceptions import ChannelNotFoundByIdError
from app.domain.playlists.entities import Playlist, PlaylistItem
from app.domain.playlists.exceptions import PlaylistNotFoundError, VideoAlreadyAddedToPlaylistError
from app.domain.playlists.repo import IPlaylistItemRepo, IPlaylistRepo
from app.domain.videos.exceptions import VideoNotFoundError
from app.infrastructure.sqlalchemy.models.videos import PlaylistItemORM, PlaylistORM
from app.infrastructure.sqlalchemy.repos.base import SARepo


class SAPlaylistRepo(SARepo, IPlaylistRepo):
    def _parse_db_error(self, error: DBAPIError, playlist: Playlist) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'playlists_channel_id_fkey':
                raise ChannelNotFoundByIdError(channel_id=playlist.channel_id) from error
            case _:
                raise

    async def create(self, playlist: Playlist) -> Playlist:
        model = PlaylistORM.from_entity(entity=playlist)
        self._session.add(instance=model)
        try:
            await self._session.flush(objects=(model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, playlist=playlist)
        return model.to_entity()

    async def update(self, playlist: Playlist) -> Playlist | None:
        stmt = (
            update(PlaylistORM)
            .where(PlaylistORM.id == playlist.id)
            .values(
                title=playlist.title,
                description=playlist.description,
                privacy_status=playlist.privacy_status.value,
            )
            .returning(PlaylistORM)
        )
        result = await self._session.execute(statement=stmt)
        orm_playlist = result.scalar_one_or_none()
        return orm_playlist.to_entity() if orm_playlist else None

    async def get_by_id(self, id: UUID) -> Playlist | None:
        stmt = select(PlaylistORM).where(PlaylistORM.id == id)
        result = await self._session.execute(statement=stmt)
        playlist = result.scalar_one_or_none()
        return playlist.to_entity() if playlist else None

    async def delete_by_id(self, id: UUID) -> bool:
        stmt = delete(PlaylistORM).where(PlaylistORM.id == id)
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0


class SAPlaylistItemRepo(SARepo, IPlaylistItemRepo):
    def _parse_db_error(self, error: DBAPIError, playlist_item: PlaylistItem) -> NoReturn:
        cause: BaseException | None = getattr(error.orig, '__cause__', None)
        constraint_name: str | None = getattr(cause, 'constraint_name', None)
        if cause is None or constraint_name is None:
            raise

        match constraint_name:
            case 'unique_playlist_item':
                raise VideoAlreadyAddedToPlaylistError(
                    playlist_id=playlist_item.playlist_id,
                    video_id=playlist_item.video_id,
                ) from error
            case 'playlist_items_playlist_id_fkey':
                raise PlaylistNotFoundError(playlist_id=playlist_item.playlist_id) from error
            case 'playlist_items_video_id_fkey':
                raise VideoNotFoundError(video_id=playlist_item.video_id) from error
            case _:
                raise

    async def create(self, playlist_item: PlaylistItem) -> PlaylistItem:
        model = PlaylistItemORM.from_entity(entity=playlist_item)
        self._session.add(instance=model)
        try:
            await self._session.flush(objects=(model,))
        except IntegrityError as e:
            self._parse_db_error(error=e, playlist_item=playlist_item)
        return model.to_entity()

    async def delete(self, playlist_id: UUID, video_id: str) -> bool:
        stmt = delete(PlaylistItemORM).where(
            PlaylistItemORM.playlist_id == playlist_id,
            PlaylistItemORM.video_id == video_id,
        )
        result = await self._session.execute(statement=stmt)
        return result.rowcount > 0
