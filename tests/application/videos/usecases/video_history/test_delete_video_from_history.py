import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoFromHistoryUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.exceptions import VideoNotFoundInHistoryError
from app.infrastructure.sqlalchemy.models import VideoHistoryItemORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import DeleteVideoFromHistoryCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoHistoryItemORMFactory, VideoORMFactory


@pytest.mark.asyncio
async def test_delete_video_from_history_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoFromHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)
        video_history_item = await VideoHistoryItemORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_id=video.id,
        )

        command = DeleteVideoFromHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)
        stmt = select(exists().where(VideoHistoryItemORM.id == video_history_item.id))

        is_video_in_history = (await session.execute(stmt)).scalar_one()
        assert is_video_in_history

        result = await use_case.execute(command=command)

        assert result is None

        is_video_in_history = (await session.execute(stmt)).scalar_one()
        assert not is_video_in_history


@pytest.mark.asyncio
async def test_delete_video_from_history_raises_error_if_video_not_found_in_history(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoFromHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)

        command = DeleteVideoFromHistoryCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoNotFoundInHistoryError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_from_history_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoFromHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = DeleteVideoFromHistoryCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_from_history_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoFromHistoryUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = DeleteVideoFromHistoryCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_from_history_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoFromHistoryUseCase)
        command = DeleteVideoFromHistoryCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
