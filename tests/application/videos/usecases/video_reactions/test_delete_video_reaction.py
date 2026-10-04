from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoReactionUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError, VideoReactionNotFoundError
from app.infrastructure.sqlalchemy.models import VideoReactionORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import DeleteVideoReactionCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory, VideoReactionORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'privacy_status',
    [VideoPrivacyStatusEnum.PUBLIC, VideoPrivacyStatusEnum.UNLISTED],
)
async def test_delete_video_reaction_returns_none_if_deleted(
    container: AsyncContainer,
    privacy_status: VideoPrivacyStatusEnum,
):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=privacy_status,
        )
        video_reaction = await VideoReactionORMFactory.create(session=session, channel_id=channel.id, video_id=video.id)

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        stmt = select(exists().where(VideoReactionORM.id == video_reaction.id))

        is_reaction_exists = (await session.execute(statement=stmt)).scalar_one()
        assert is_reaction_exists

        result = await use_case.execute(command=command)

        assert result is None

        is_reaction_exists = (await session.execute(statement=stmt)).scalar_one()
        assert not is_reaction_exists


@pytest.mark.asyncio
async def test_delete_video_reaction_returns_none_if_deleted_and_video_private(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
        )
        video_reaction = await VideoReactionORMFactory.create(
            session=session,
            channel_id=video_author.id,
            video_id=video.id,
        )

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        stmt = select(exists().where(VideoReactionORM.id == video_reaction.id))

        is_reaction_exists = (await session.execute(statement=stmt)).scalar_one()
        assert is_reaction_exists

        result = await use_case.execute(command=command)

        assert result is None

        is_reaction_exists = (await session.execute(statement=stmt)).scalar_one()
        assert not is_reaction_exists


@pytest.mark.asyncio
async def test_delete_video_reaction_raises_error_if_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE,
        )

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id
        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_delete_video_reaction_raises_error_if_reaction_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
        )

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        with pytest.raises(VideoReactionNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
@pytest.mark.parametrize('upload_status', [VideoUploadStatusEnum.PENDING, VideoUploadStatusEnum.UPLOADING])
async def test_delete_video_reaction_raises_error_if_video_not_completed(
    container: AsyncContainer,
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=upload_status,
        )

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_delete_video_reaction_raises_error_if_video_author_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC,
        )

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_delete_video_reaction_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_delete_video_reaction_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = DeleteVideoReactionCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_delete_video_reaction_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoReactionUseCase)

        channel_id = uuid7()
        command = DeleteVideoReactionCommandFactory.build(current_channel_id=channel_id)

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel_id
