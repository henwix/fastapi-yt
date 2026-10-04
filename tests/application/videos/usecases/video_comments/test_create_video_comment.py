from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import CreateVideoCommentUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.entities import VideoComment
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoCommentNotFoundError, VideoNotFoundError
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import CreateVideoCommentCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoCommentORMFactory, VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize('privacy_status', [VideoPrivacyStatusEnum.PUBLIC, VideoPrivacyStatusEnum.UNLISTED])
async def test_create_video_comment_returns_correct_entity_if_created(
    container: AsyncContainer, privacy_status: VideoPrivacyStatusEnum
):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=privacy_status,
        )

        command = CreateVideoCommentCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoComment)

        assert result.video_id == command.video_id
        assert result.channel_id == command.current_channel_id
        assert result.reply_comment_id is None
        assert result.text == command.text
        assert result.reply_level == 0


@pytest.mark.asyncio
@pytest.mark.parametrize('privacy_status', [VideoPrivacyStatusEnum.PUBLIC, VideoPrivacyStatusEnum.UNLISTED])
async def test_create_video_comment_with_reply_returns_correct_entity_if_created(
    container: AsyncContainer, privacy_status: VideoPrivacyStatusEnum
):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=privacy_status,
        )
        video_comment = await VideoCommentORMFactory.create(session=session, channel_id=channel.id, video_id=video.id)

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
            reply_comment_id=video_comment.id,
        )

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoComment)

        assert result.video_id == command.video_id
        assert result.channel_id == command.current_channel_id
        assert result.reply_comment_id == video_comment.id
        assert result.text == command.text
        assert result.reply_level == video_comment.reply_level + 1


@pytest.mark.asyncio
async def test_create_video_comment_returns_correct_entity_if_created_and_video_private(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
        )

        command = CreateVideoCommentCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoComment)

        assert result.video_id == command.video_id
        assert result.channel_id == command.current_channel_id
        assert result.reply_comment_id is None
        assert result.text == command.text
        assert result.reply_level == 0


@pytest.mark.asyncio
async def test_create_video_comment_with_reply_returns_correct_entity_if_created_and_video_private(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
        )
        video_comment = await VideoCommentORMFactory.create(session=session, channel_id=channel.id, video_id=video.id)

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=video_author.id,
            video_id=video.id,
            reply_comment_id=video_comment.id,
        )

        result = await use_case.execute(command=command)

        assert isinstance(result, VideoComment)

        assert result.video_id == command.video_id
        assert result.channel_id == command.current_channel_id
        assert result.reply_comment_id == video_comment.id
        assert result.text == command.text
        assert result.reply_level == video_comment.reply_level + 1


@pytest.mark.asyncio
async def test_create_video_comment_with_reply_raises_error_if_reply_comment_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
            reply_comment_id=uuid7(),
        )

        with pytest.raises(VideoCommentNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_comment_id == command.reply_comment_id


@pytest.mark.asyncio
async def test_create_video_comment_raises_error_if_access_forbidden(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
        )

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id
        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
@pytest.mark.parametrize('upload_status', [VideoUploadStatusEnum.PENDING, VideoUploadStatusEnum.UPLOADING])
async def test_create_video_comment_raises_error_if_video_not_completed(
    container: AsyncContainer, upload_status: VideoUploadStatusEnum
):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=upload_status,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_create_video_comment_raises_error_if_video_author_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_create_video_comment_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
        )

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_create_video_comment_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
        )

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_create_video_comment_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = CreateVideoCommentCommandFactory.build(
            current_channel_id=channel.id,
        )

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_create_video_comment_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoCommentUseCase)

        channel_id = uuid7()
        command = CreateVideoCommentCommandFactory.build(current_channel_id=channel_id)

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel_id
