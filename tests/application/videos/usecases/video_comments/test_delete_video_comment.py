import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoCommentUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.exceptions import VideoCommentAccessForbiddenError, VideoCommentNotFoundError
from app.infrastructure.sqlalchemy.models import VideoCommentORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import DeleteVideoCommentCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoCommentORMFactory, VideoORMFactory


@pytest.mark.asyncio
async def test_delete_video_comment_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoCommentUseCase)
        session = await di.get(AsyncSession)

        comment_author = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)
        video_comment = await VideoCommentORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=comment_author.id,
        )

        command = DeleteVideoCommentCommandFactory.build(
            current_channel_id=comment_author.id,
            video_comment_id=video_comment.id,
        )
        stmt = select(exists().where(VideoCommentORM.id == video_comment.id))

        is_comment_exists = (await session.execute(statement=stmt)).scalar_one()
        assert is_comment_exists

        result = await use_case.execute(command=command)

        assert result is None

        is_comment_exists = (await session.execute(statement=stmt)).scalar_one()
        assert not is_comment_exists


@pytest.mark.asyncio
async def test_delete_video_comment_raises_error_if_video_comment_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoCommentUseCase)
        session = await di.get(AsyncSession)

        comment_author = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)
        video_comment = await VideoCommentORMFactory.create(
            session=session,
            video_id=video.id,
            channel_id=comment_author.id,
        )

        command = DeleteVideoCommentCommandFactory.build(
            current_channel_id=video_author.id,
            video_comment_id=video_comment.id,
        )

        with pytest.raises(VideoCommentAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == video_author.id
        assert e.value.video_comment_id == video_comment.id


@pytest.mark.asyncio
async def test_delete_video_comment_raises_error_if_video_comment_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = DeleteVideoCommentCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(VideoCommentNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_comment_id == command.video_comment_id


@pytest.mark.asyncio
async def test_delete_video_comment_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = DeleteVideoCommentCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_comment_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = DeleteVideoCommentCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_comment_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoCommentUseCase)

        command = DeleteVideoCommentCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
