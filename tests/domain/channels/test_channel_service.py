import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoNotFoundError
from app.domain.videos.services import IVideoService
from app.utils.datetime import get_current_utc_datetime
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

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session, channel_id=channel.id, upload_status=VideoUploadStatusEnum.COMPLETED
        )

        with pytest.raises(VideoNotFoundError) as e:
            await service.try_get_completed_by_id(id=video.id)

        assert e.value.video_id == video.id
