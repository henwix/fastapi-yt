from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import GenerateVideoDownloadUrlUseCase
from app.core.configs import settings
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoFileNotFoundError, VideoNotFoundError
from tests.factories.commands.videos import GenerateVideoDownloadUrlCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_generate_video_download_url_returns_correct_url_if_video_public_and_channel_not_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=None, video_id=video.id)

        url = await use_case.execute(command=command)
        assert url.startswith(f'{settings.s3_endpoint}/{video_file.bucket}/{video_file.key}')
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=10800' in url


@pytest.mark.asyncio
async def test_generate_video_download_url_returns_correct_url_if_video_unlisted_and_channel_not_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.UNLISTED.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=None, video_id=video.id)

        url = await use_case.execute(command=command)
        assert url.startswith(f'{settings.s3_endpoint}/{video_file.bucket}/{video_file.key}')
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=10800' in url


@pytest.mark.asyncio
async def test_generate_video_download_url_returns_correct_url_if_video_private_and_channel_is_author(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        url = await use_case.execute(command=command)
        assert url.startswith(f'{settings.s3_endpoint}/{video_file.bucket}/{video_file.key}')
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=10800' in url


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_channel_not_authenticated(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=None, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_channel_not_author(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=second_channel.id, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_channel_not_active(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_private_and_channel_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=uuid7(), video_id=video.id)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_file_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=None, video_id=video.id)

        with pytest.raises(VideoFileNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_file_not_found_in_db(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        video_file = await FileORMFactory.create(session=session)
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PUBLIC.value,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=None, video_id=video.id)

        with (  # noqa: PT012
            pytest.raises(VideoFileNotFoundError) as e,
            patch.object(use_case._file_service, 'get_by_id') as mock_file_service,
        ):
            mock_file_service.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=video_file)

        mock_file_service.assert_called_once_with(id=video_file.id)
        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_not_found(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)

        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=uuid7())

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_not_uploaded(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            privacy_status=VideoPrivacyStatusEnum.PRIVATE.value,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=uuid7(), video_id=video.id)

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_channel_author_deleted(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=uuid7(), video_id=video.id)

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_download_url_raises_error_if_video_channel_author_deletion_status_purging(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoDownloadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
        )
        command = GenerateVideoDownloadUrlCommandFactory.build(current_channel_id=uuid7(), video_id=video.id)

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)
