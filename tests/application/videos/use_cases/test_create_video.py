import pytest
from dishka import AsyncContainer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.create_video import CreateVideoUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.entities import Video
from app.domain.videos.enums import VideoUploadStatusEnum
from app.infrastructure.sqlalchemy.models.videos import VideoORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import CreateVideoCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
async def test_create_video_returns_correct_entity_if_created(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = CreateVideoCommandFactory.build(current_channel_id=channel.id)

        result = await use_case.execute(command=command)
        stmt = select(VideoORM).where(VideoORM.id == result.id)
        db_video = (await session.execute(statement=stmt)).scalar_one()

        assert isinstance(result, Video)
        assert len(result.id) == 11
        assert result.channel_id == channel.id
        assert result.title == command.title
        assert result.description == command.description
        assert result.privacy_status is command.privacy_status
        assert not result.is_reported
        assert result.created_at < get_current_utc_datetime()
        assert result.views_count == 0
        assert result.upload_id is None
        assert result.s3_key is None
        assert result.upload_status is VideoUploadStatusEnum.PENDING

        assert len(db_video.id) == 11
        assert db_video.channel_id == channel.id
        assert db_video.title == command.title
        assert db_video.description == command.description
        assert db_video.privacy_status == command.privacy_status.value
        assert not db_video.is_reported
        assert db_video.created_at < get_current_utc_datetime()
        assert db_video.views_count == 0
        assert db_video.upload_id is None
        assert db_video.s3_key is None
        assert db_video.upload_status == VideoUploadStatusEnum.PENDING.value


@pytest.mark.asyncio
async def test_create_video_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = CreateVideoCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoUseCase)

        command = CreateVideoCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
