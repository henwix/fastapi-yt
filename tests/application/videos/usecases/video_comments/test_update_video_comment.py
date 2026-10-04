import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import UpdateVideoCommentUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.entities import VideoComment
from app.domain.videos.exceptions import VideoCommentAccessForbiddenError, VideoCommentNotFoundError
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import UpdateVideoCommentCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoCommentORMFactory, VideoORMFactory


@pytest.mark.asyncio
async def test_update_video_comment_returns_correct_entity_if_updated(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        comment_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)
        video_comment = await VideoCommentORMFactory.create(
            session=session,
            channel_id=comment_author.id,
            video_id=video.id,
            is_edited=False,
        )

        command = UpdateVideoCommentCommandFactory.build(
            current_channel_id=comment_author.id,
            video_comment_id=video_comment.id,
        )

        assert not video_comment.is_edited

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoComment)

        assert result.text == command.text
        assert video_comment.text == command.text

        assert result.id == video_comment.id
        assert result.video_id == video_comment.video_id
        assert result.channel_id == video_comment.channel_id
        assert result.reply_comment_id == video_comment.reply_comment_id
        assert result.is_edited == video_comment.is_edited
        assert result.reply_level == video_comment.reply_level
        assert result.created_at == video_comment.created_at
        assert result.is_edited


@pytest.mark.asyncio
async def test_update_video_comment_raises_error_if_video_comment_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        comment_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)
        video_comment = await VideoCommentORMFactory.create(
            session=session,
            channel_id=comment_author.id,
            video_id=video.id,
            is_edited=False,
        )

        command = UpdateVideoCommentCommandFactory.build(
            current_channel_id=video_author.id,
            video_comment_id=video_comment.id,
        )

        with pytest.raises(VideoCommentAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == video_author.id
        assert e.value.video_comment_id == video_comment.id


@pytest.mark.asyncio
async def test_update_video_comment_raises_error_if_video_comment_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = UpdateVideoCommentCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(VideoCommentNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_comment_id == command.video_comment_id


@pytest.mark.asyncio
async def test_update_video_comment_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = UpdateVideoCommentCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_update_video_comment_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = UpdateVideoCommentCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_update_video_comment_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(UpdateVideoCommentUseCase)

        command = UpdateVideoCommentCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
