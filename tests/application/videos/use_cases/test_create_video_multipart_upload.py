import secrets

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.create_video_multipart_upload import CreateVideoMultipartUploadUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidFileFormatError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
    VideoUploadAlreadyCreatedError,
)
from tests.factories.commands.videos import CreateVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected_filename',
    ['test.mp4', 'test.mkv', 'test.mov', 'test.webm', 'test.MP4', 'test.MKV', 'test.MOV', 'test.WEBM'],
)
async def test_create_video_multipart_upload_returns_none_if_created(
    mock_container: AsyncContainer,
    expected_filename: str,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.PENDING,
            s3_key=None,
            upload_id=None,
        )
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            filename=expected_filename,
            video_id=video.id,
        )

        expected_upload_id = secrets.token_hex(16)
        use_case._s3_service.UPLOAD_ID = expected_upload_id

        result = await use_case.execute(command=command)

        assert result is None
        assert video.upload_id == expected_upload_id
        assert video.upload_status == VideoUploadStatusEnum.UPLOADING.value
        assert video.s3_key.startswith(settings.s3_videos_key_prefix) and video.s3_key.endswith(command.filename)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_upload_already_completed(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            upload_id=None,
        )
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_video_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_video_access_forbidden(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.PENDING,
        )
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_upload_already_created(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING,
        )
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_filename', ['test.png', 'test.jpg', 'test.webp', 'test.gif', 'test.GIF', 'test.JPG'])
async def test_create_video_multipart_upload_raises_error_if_invalid_video_format(
    mock_container: AsyncContainer,
    expected_filename: str,
):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            filename=expected_filename,
        )

        with pytest.raises(VideoInvalidFileFormatError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = CreateVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)

        command = CreateVideoMultipartUploadCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
