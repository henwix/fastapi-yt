from datetime import datetime
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelDeletionFailedError, ChannelRestorationFailedError
from app.domain.channels.services import IChannelService
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoNotFoundError
from app.domain.videos.services import IVideoService
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_get_completed_by_id_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IVideoService)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session, channel_id=channel.id, upload_status=VideoUploadStatusEnum.COMPLETED
        )

        result = await service.try_get_completed_by_id(id=video.id)

        assert result.id == video.id
        assert result.channel_id == video.channel_id
        assert result.title == video.title
        assert result.description == video.description
        assert result.privacy_status == video.privacy_status
        assert result.is_reported == video.is_reported
        assert result.created_at == video.created_at
        assert result.views_count == video.views_count
        assert result.upload_id == video.upload_id
        assert result.s3_key == video.s3_key
        assert result.thumbnail_s3_key == video.thumbnail_s3_key
        assert result.upload_status == video.upload_status


@pytest.mark.asyncio
@pytest.mark.parametrize('upload_status', [VideoUploadStatusEnum.PENDING, VideoUploadStatusEnum.UPLOADING])
async def test_get_completed_by_id_raises_error_if_not_completed(
    container: AsyncContainer,
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        service = await di.get(IVideoService)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=channel.id, upload_status=upload_status)

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video.id)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_get_completed_by_id_raises_error_if_video_author_deleted(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IVideoService)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)
        video = await VideoORMFactory.create(
            session=session, channel_id=channel.id, upload_status=VideoUploadStatusEnum.COMPLETED
        )

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video.id)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_restore_channel_returns_none_if_restored(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IChannelService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create_deleted(session=session)

        result = await service.try_restore(id=channel.id)

        await session.refresh(instance=channel)

        assert result is None
        assert channel.deleted_at is None
        assert channel.deletion_status == ChannelDeletionStatusEnum.ACTIVE.value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'deletion_status',
    [
        ChannelDeletionStatusEnum.ACTIVE.value,
        ChannelDeletionStatusEnum.PURGING.value,
    ],
)
async def test_restore_channel_raises_error_if_channel_deletion_status_is_active_or_purging(
    container: AsyncContainer,
    deletion_status: str,
):
    async with container() as di:
        service = await di.get(IChannelService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, deletion_status=deletion_status)

        with pytest.raises(ChannelRestorationFailedError) as e:
            await service.try_restore(id=channel.id)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_restore_channel_raises_error_if_channel_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        service = await di.get(IChannelService)

        channel_id = uuid7()
        with pytest.raises(ChannelRestorationFailedError) as e:
            await service.try_restore(id=channel_id)

        assert e.value.channel_id == channel_id


@pytest.mark.asyncio
async def test_delete_channel_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IChannelService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        result = await service.try_delete(id=channel.id)

        await session.refresh(instance=channel)

        assert result is None
        assert isinstance(channel.deleted_at, datetime)
        assert channel.deletion_status == ChannelDeletionStatusEnum.DELETED.value


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'deletion_status',
    [
        ChannelDeletionStatusEnum.DELETED.value,
        ChannelDeletionStatusEnum.PURGING.value,
    ],
)
async def test_delete_channel_raises_error_if_channel_deletion_status_is_deleted_or_purging(
    container: AsyncContainer,
    deletion_status: str,
):
    async with container() as di:
        service = await di.get(IChannelService)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, deletion_status=deletion_status)

        with pytest.raises(ChannelDeletionFailedError) as e:
            await service.try_delete(id=channel.id)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_delete_channel_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IChannelService)
        channel_id = uuid7()

        with pytest.raises(ChannelDeletionFailedError) as e:
            await service.try_delete(id=channel_id)

        assert e.value.channel_id == channel_id
