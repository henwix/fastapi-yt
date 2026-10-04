import pytest
import sqlalchemy as sa
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import ClearVideoHistoryUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.exceptions import VideoHistoryEmptyError
from app.infrastructure.sqlalchemy.models import VideoHistoryItemORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import ClearVideoHistoryCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoHistoryItemORMFactory, VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('videos_count', [1, 3, 6, 12, 30, 40])
async def test_clear_history_returns_none_if_cleared(container: AsyncContainer, videos_count: int):
    async with container() as di:
        use_case = await di.get(ClearVideoHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)

        videos = await VideoORMFactory.create_batch(session=session, size=videos_count, channel_id=video_author.id)
        video_history_items = []
        for video in videos:
            video_history_item = VideoHistoryItemORMFactory.build(channel_id=channel.id, video_id=video.id)
            video_history_items.append(video_history_item)

        session.add_all(instances=video_history_items)
        await session.commit()

        command = ClearVideoHistoryCommandFactory.build(current_channel_id=channel.id)

        stmt = sa.select(sa.func.count()).where(VideoHistoryItemORM.channel_id == channel.id)

        db_videos_count = (await session.execute(statement=stmt)).scalar_one()
        assert db_videos_count == videos_count

        result = await use_case.execute(command=command)

        assert result is None

        db_videos_count = (await session.execute(statement=stmt)).scalar_one()
        assert db_videos_count == 0


@pytest.mark.asyncio
async def test_clear_history_raises_error_if_history_is_empty(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ClearVideoHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        channel_id = channel.id

        command = ClearVideoHistoryCommandFactory.build(current_channel_id=channel_id)

        with pytest.raises(VideoHistoryEmptyError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel_id


@pytest.mark.asyncio
async def test_clear_history_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ClearVideoHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = ClearVideoHistoryCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_clear_history_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ClearVideoHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = ClearVideoHistoryCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_clear_history_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(ClearVideoHistoryUseCase)

        command = ClearVideoHistoryCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
