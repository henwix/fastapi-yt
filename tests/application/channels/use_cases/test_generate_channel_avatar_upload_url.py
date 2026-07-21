import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.channels.use_cases.generate_channel_avatar_upload_url import GenerateChannelAvatarUploadUrlUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import (
    ChannelAvatarInvalidFileFormatError,
    ChannelNotActiveError,
    ChannelNotFoundByIdError,
)
from tests.factories.commands.channels import GenerateChannelAvatarUploadUrlCommandFactory
from tests.factories.models.channels import ChannelORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected_filename', ['test.png', 'test.jpg', 'test.jpeg', 'test.PNG', 'test.JPG', 'test.JPEG']
)
async def test_generate_channel_avatar_upload_url_returns_correct_data(
    container: AsyncContainer,
    expected_filename: str,
):
    async with container() as di:
        use_case = await di.get(GenerateChannelAvatarUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = GenerateChannelAvatarUploadUrlCommandFactory.build(
            current_channel_id=channel.id,
            filename=expected_filename,
        )

        url, key, channel_id = await use_case.execute(command=command)

        assert url.startswith(f'{settings.s3_endpoint}/{settings.s3_public_bucket_name}/{key}')
        assert 'amz-meta-channel_id' in url
        assert 'X-Amz-Signature' in url
        assert 'Amz-Expires' in url
        assert key.startswith(settings.s3_avatars_key_prefix) and key.endswith(expected_filename)
        assert channel_id == channel.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'expected_filename', ['test', 'test.mp4', 'test.mov', 'test.gif', 'test.test', 'test.MP4', 'test.GIF']
)
async def test_generate_channel_avatar_upload_url_raises_error_if_filename_invalid(
    container: AsyncContainer,
    expected_filename: str,
):
    async with container() as di:
        use_case = await di.get(GenerateChannelAvatarUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = GenerateChannelAvatarUploadUrlCommandFactory.build(
            current_channel_id=channel.id,
            filename=expected_filename,
        )

        with pytest.raises(ChannelAvatarInvalidFileFormatError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_channel_avatar_upload_url_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateChannelAvatarUploadUrlUseCase)

        command = GenerateChannelAvatarUploadUrlCommandFactory.build(filename='test.png')

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_channel_avatar_upload_url_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateChannelAvatarUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = GenerateChannelAvatarUploadUrlCommandFactory.build(
            current_channel_id=channel.id,
            filename='test.png',
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)
