import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoDeletionStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoNotFoundError
from app.domain.videos.services import IVideoService
from app.utils.videos import generate_video_id
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_try_get_by_id_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        session = await di.get(AsyncSession)
        service = await di.get(IVideoService)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            title='test_title',
            description='test_description',
            deletion_status=VideoDeletionStatusEnum.ACTIVE.value,
        )

        result = await service.try_get_by_id(id=video.id)

        assert isinstance(result, Video)

        assert result.channel_id == video.channel_id
        assert result.title == video.title
        assert result.description == video.description
        assert result.privacy_status.value == video.privacy_status
        assert result.is_reported == video.is_reported
        assert result.created_at == video.created_at
        assert result.views_count == video.views_count
        assert result.upload_id == video.upload_id
        assert result.upload_status == video.upload_status
        assert result.deletion_status.value == video.deletion_status
        assert result.locked_until == video.locked_until
        assert result.video_file_id == video.video_file_id
        assert result.thumbnail_file_id == video.thumbnail_file_id


@pytest.mark.asyncio
async def test_try_get_by_id_raises_error_if_video_deletion_status_deleted(container: AsyncContainer):
    async with container() as di:
        session = await di.get(AsyncSession)
        service = await di.get(IVideoService)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            deletion_status=VideoDeletionStatusEnum.DELETED.value,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_by_id(id=video.id)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_try_get_by_id_raises_error_if_video_not_found_by_id(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IVideoService)
        video_id = generate_video_id()

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_by_id(id=video_id)

        assert e.value.video_id == video_id


@pytest.mark.asyncio
async def test_try_get_completed_by_id_returns_correct_entity(container: AsyncContainer):
    async with container() as di:
        session = await di.get(AsyncSession)
        service = await di.get(IVideoService)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            title='test_title',
            description='test_description',
            deletion_status=VideoDeletionStatusEnum.ACTIVE.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
        )

        result = await service.try_get_completed_by_id(id=video.id)

        assert isinstance(result, Video)

        assert result.channel_id == video.channel_id
        assert result.title == video.title
        assert result.description == video.description
        assert result.privacy_status.value == video.privacy_status
        assert result.is_reported == video.is_reported
        assert result.created_at == video.created_at
        assert result.views_count == video.views_count
        assert result.upload_id == video.upload_id
        assert result.upload_status == video.upload_status
        assert result.deletion_status.value == video.deletion_status
        assert result.locked_until == video.locked_until
        assert result.video_file_id == video.video_file_id
        assert result.thumbnail_file_id == video.thumbnail_file_id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('upload_status', 'deletion_status'),
    [
        (VideoUploadStatusEnum.PENDING.value, VideoDeletionStatusEnum.ACTIVE.value),
        (VideoUploadStatusEnum.UPLOADING.value, VideoDeletionStatusEnum.ACTIVE.value),
        (VideoUploadStatusEnum.COMPLETED.value, VideoDeletionStatusEnum.DELETED.value),
    ],
)
async def test_try_get_completed_by_id_raises_error_if_video_invalid_status(
    container: AsyncContainer,
    upload_status: str,
    deletion_status: str,
):
    async with container() as di:
        session = await di.get(AsyncSession)
        service = await di.get(IVideoService)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=upload_status,
            deletion_status=deletion_status,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video.id)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_try_get_completed_by_id_raises_error_if_video_not_found_by_id(container: AsyncContainer):
    async with container() as di:
        service = await di.get(IVideoService)
        video_id = generate_video_id()

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video_id)

        assert e.value.video_id == video_id


@pytest.mark.asyncio
async def test_try_get_completed_by_id_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        session = await di.get(AsyncSession)
        service = await di.get(IVideoService)
        channel = await ChannelORMFactory.create_deleted(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            deletion_status=VideoDeletionStatusEnum.ACTIVE.value,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video.id)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_try_get_completed_by_id_raises_error_if_channel_deletion_status_purging(container: AsyncContainer):
    async with container() as di:
        session = await di.get(AsyncSession)
        service = await di.get(IVideoService)
        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            deletion_status=VideoDeletionStatusEnum.ACTIVE.value,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video.id)

        assert e.value.video_id == video.id
