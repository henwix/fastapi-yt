from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.playlists.entities import Playlist
from app.domain.playlists.exceptions import PlaylistNotFoundError
from app.domain.playlists.services import IPlaylistService
from app.utils.datetime import get_current_utc_datetime
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import PlaylistORMFactory


@pytest.mark.asyncio
async def test_try_existing_get_by_id_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IPlaylistService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        playlist = await PlaylistORMFactory.create(session=session, channel_id=channel.id)

        result = await service.try_existing_get_by_id(id=playlist.id)

        assert isinstance(result, Playlist)
        assert result.id == playlist.id
        assert result.title == playlist.title
        assert result.description == playlist.description
        assert result.privacy_status.value == playlist.privacy_status
        assert result.channel_id == playlist.channel_id
        assert result.created_at == playlist.created_at


@pytest.mark.asyncio
async def test_try_existing_get_by_id_raises_error_if_playlist_author_channel_deleted(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IPlaylistService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        playlist = await PlaylistORMFactory.create(session=session, channel_id=channel.id)

        with pytest.raises(PlaylistNotFoundError) as e:
            await service.try_existing_get_by_id(id=playlist.id)

        assert e.value.playlist_id == playlist.id


@pytest.mark.asyncio
async def test_try_existing_get_by_id_raises_error_if_playlist_not_found(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IPlaylistService)

        playlist_id = uuid7()
        with pytest.raises(PlaylistNotFoundError) as e:
            await service.try_existing_get_by_id(id=playlist_id)

        assert e.value.playlist_id == playlist_id
