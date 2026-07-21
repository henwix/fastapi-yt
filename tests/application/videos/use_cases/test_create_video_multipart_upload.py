import re
from uuid import uuid4

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.create_video_multipart_upload import CreateVideoMultipartUploadUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.constants import VIDEO_ID_PATTERN
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoInvalidFileFormatError
from tests.factories.commands.videos import CreateVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected_filename',
    ['test.mp4', 'test.mkv', 'test.mov', 'test.webm', 'test.MP4', 'test.MKV', 'test.MOV', 'test.WEBM'],
)
async def test_create_video_multipart_upload_returns_correct_entity(
    container: AsyncContainer,
    expected_filename: str,
):
    async with container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = CreateVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            filename=expected_filename,
        )

        expected_upload_id = uuid4().hex
        use_case._s3_provider.UPLOAD_ID = expected_upload_id

        video = await use_case.execute(command=command)

        assert video.title == command.title
        assert video.description == command.description
        assert video.privacy_status is command.privacy_status
        assert video.channel_id == channel.id
        assert video.description == command.description
        assert video.upload_id == expected_upload_id
        assert video.s3_key.startswith(settings.s3_videos_key_prefix) and video.s3_key.endswith(command.filename)
        assert not video.is_reported
        assert video.upload_status is VideoUploadStatusEnum.UPLOADING
        assert re.fullmatch(pattern=VIDEO_ID_PATTERN, string=video.id)


@pytest.mark.asyncio
@pytest.mark.parametrize('expected_filename', ['test.png', 'test.jpg', 'test.webp', 'test.gif', 'test.GIF', 'test.JPG'])
async def test_create_video_multipart_upload_raises_error_if_invalid_video_format(
    container: AsyncContainer,
    expected_filename: str,
):
    async with container() as di:
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
async def test_create_video_multipart_upload_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = CreateVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_create_video_multipart_upload_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CreateVideoMultipartUploadUseCase)

        command = CreateVideoMultipartUploadCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)
