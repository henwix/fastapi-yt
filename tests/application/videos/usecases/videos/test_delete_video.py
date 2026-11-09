from datetime import timedelta
from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoDeletionStatusEnum, VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import DeleteVideoCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('privacy_status', 'upload_status'),
    [
        (VideoPrivacyStatusEnum.PUBLIC, VideoUploadStatusEnum.COMPLETED),
        (VideoPrivacyStatusEnum.PUBLIC, VideoUploadStatusEnum.PENDING),
        (VideoPrivacyStatusEnum.PUBLIC, VideoUploadStatusEnum.UPLOADING),
        (VideoPrivacyStatusEnum.PRIVATE, VideoUploadStatusEnum.COMPLETED),
        (VideoPrivacyStatusEnum.PRIVATE, VideoUploadStatusEnum.PENDING),
        (VideoPrivacyStatusEnum.PRIVATE, VideoUploadStatusEnum.UPLOADING),
        (VideoPrivacyStatusEnum.UNLISTED, VideoUploadStatusEnum.COMPLETED),
        (VideoPrivacyStatusEnum.UNLISTED, VideoUploadStatusEnum.PENDING),
        (VideoPrivacyStatusEnum.UNLISTED, VideoUploadStatusEnum.UPLOADING),
    ],
)
async def test_delete_video_returns_none_if_deleted(
    container: AsyncContainer,
    privacy_status: VideoPrivacyStatusEnum,
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=privacy_status,
            upload_status=upload_status,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        result = await use_case.execute(command=command)

        await session.refresh(instance=video)

        assert result is None

        assert video.deletion_status == VideoDeletionStatusEnum.DELETED.value
        assert video.locked_until is not None
        assert video.locked_until > get_current_utc_datetime()
        assert video.locked_until < get_current_utc_datetime() + timedelta(minutes=5)


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_video_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)

        command = DeleteVideoCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session)

        command = DeleteVideoCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create_deleted(session=session)

        command = DeleteVideoCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = DeleteVideoCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)

        command = DeleteVideoCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_video_not_updated(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)

        with (  # noqa: PT012
            patch.object(use_case._video_service._repo, 'soft_delete_by_id') as video_repo_mock,
            pytest.raises(VideoNotFoundError) as e,
        ):
            video_repo_mock.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=video)

        assert e.value.video_id == video.id
