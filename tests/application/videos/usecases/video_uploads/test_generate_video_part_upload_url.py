import secrets
from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import GenerateVideoPartUploadUrlUseCase
from app.core.configs import settings
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
    VideoUploadNotCreatedError,
)
from app.utils.videos import generate_video_id
from tests.factories.commands.videos import GenerateVideoPartUploadUrlCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_returns_correct_url(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        expected_bucket = settings.s3_private_bucket_name
        video_file = await FileORMFactory.create(
            session=session,
            key=f'videos/{secrets.token_hex(4)}_test.mp4',
            bucket=expected_bucket,
        )
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        url = await use_case.execute(command=command)

        assert url.startswith(f'{settings.s3_endpoint}/{expected_bucket}/{video_file.key}')
        assert f'uploadId={video.upload_id}' in url
        assert f'partNumber={command.part_number}' in url
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=120' in url


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_channel_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_channel_deletion_status_purging(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)

        command = GenerateVideoPartUploadUrlCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = GenerateVideoPartUploadUrlCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_access_forbidden(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(
            current_channel_id=second_channel.id, video_id=video.id
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_already_uploaded(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_upload_not_created_and_status_pending(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.PENDING,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_file_not_found_in_db(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        expected_bucket = settings.s3_private_bucket_name
        video_file = await FileORMFactory.create(
            session=session,
            key=f'videos/{secrets.token_hex(4)}_test.mp4',
            bucket=expected_bucket,
        )
        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with (  # noqa: PT012
            pytest.raises(VideoUploadNotCreatedError) as e,
            patch.object(use_case._file_service, 'get_by_id') as file_service_mock,
        ):
            file_service_mock.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=video)
        await session.refresh(instance=video_file)

        file_service_mock.assert_called_once_with(id=video_file.id)
        assert e.value.video_id == video.id


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_uploading_and_upload_id_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=None,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_uploading_status_and_file_id_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=None,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)
