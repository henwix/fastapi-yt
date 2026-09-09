from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.abort_video_multipart_upload import AbortVideoMultipartUploadUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
    VideoUploadNotCreatedError,
)
from app.utils.videos import generate_video_id
from tests.factories.commands.videos import AbortVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_upload_aborted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with patch.object(use_case._s3_service, 'schedule_abort_multipart_upload') as mock_abort_multipart:
            await use_case.execute(command=command)

        mock_abort_multipart.assert_called_once()
        assert video.upload_status == VideoUploadStatusEnum.PENDING.value
        assert video.upload_id is None
        assert video.s3_key is None


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)

        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=generate_video_id(),
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_video_access_forbidden(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_video_already_uploaded(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_upload_not_created_and_status_pending(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.PENDING.value,
            upload_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_upload_not_created_and_upload_id_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_upload_not_created_and_s3_key_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            s3_key=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)
