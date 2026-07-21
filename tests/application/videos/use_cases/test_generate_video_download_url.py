from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.generate_video_download_url import GenerateVideoDownloadUrlUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.utils.videos import generate_video_id
from tests.factories.commands.videos import GenerateVideoDownloadUrlCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_generate_video_download_url_returns_correct_url_if_video_public_and_user_not_authenticated(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=None,
            video_id=video.id,
        )

        url = await use_case.execute(command=command)
        assert url.startswith(f'{settings.s3_endpoint}/{settings.s3_private_bucket_name}/{video.s3_key}')
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=10800' in url


@pytest.mark.asyncio
async def test_generate_video_download_url_returns_correct_url_if_video_unlisted_and_user_not_authenticated(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.UNLISTED.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=None,
            video_id=video.id,
        )

        url = await use_case.execute(command=command)
        assert url.startswith(f'{settings.s3_endpoint}/{settings.s3_private_bucket_name}/{video.s3_key}')
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=10800' in url


@pytest.mark.asyncio
async def test_generate_video_download_url_returns_correct_url_if_video_private_and_user_is_author(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        url = await use_case.execute(command=command)
        assert url.startswith(f'{settings.s3_endpoint}/{settings.s3_private_bucket_name}/{video.s3_key}')
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=10800' in url


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_user_not_authenticated(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=None,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_user_not_author(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_user_not_active(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_user_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=video.id,
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_not_found(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)

        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=generate_video_id(),
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_not_uploaded(
    container: AsyncContainer,
):
    async with container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=video.id,
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)
