from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import AbortVideoMultipartUploadUseCase
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoNotFoundError,
    VideoUploadAlreadyCompletedError,
    VideoUploadFailedToAbortError,
    VideoUploadNotCreatedError,
)
from app.infrastructure.sqlalchemy.models import FileORM
from tests.factories.commands.videos import AbortVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_upload_aborted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with patch.object(use_case._s3_service, 'schedule_abort_multipart_upload') as mock_abort_multipart:
            await use_case.execute(command=command)

        file_exists_stmt = select(exists().where(FileORM.bucket == video_file.bucket, FileORM.key == video_file.key))

        mock_abort_multipart.assert_called_once()
        assert video.video_upload_status == VideoUploadStatusEnum.PENDING.value
        assert video.video_upload_id is None
        assert video.video_file_id is None
        assert not (await session.execute(statement=file_exists_stmt)).scalar_one()


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = AbortVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)
        command = AbortVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_deletion_status_purging(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)

        command = AbortVideoMultipartUploadCommandFactory.build(current_channel_id=uuid7())

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = AbortVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

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
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_already_uploaded(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
            video_upload_id=None,
            video_file_id=video_file.id,
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
            video_upload_status=VideoUploadStatusEnum.PENDING.value,
            video_upload_id=None,
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
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_upload_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_upload_not_created_and_video_file_id_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_file_not_found_in_db(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        old_video_upload_id = video.video_upload_id

        with (  # noqa: PT012
            patch.object(use_case._file_service, 'get_by_id') as mock_file_service,
            pytest.raises(VideoUploadNotCreatedError) as e,
        ):
            mock_file_service.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=video)
        await session.refresh(instance=video_file)

        mock_file_service.assert_called_once_with(id=video_file.id)

        assert e.value.video_id == video.id
        assert video.video_upload_status == VideoUploadStatusEnum.UPLOADING.value
        assert video.video_file_id == video_file.id
        assert video.video_upload_id == old_video_upload_id


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_not_updated(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        old_video_upload_id = video.video_upload_id

        with (  # noqa: PT012
            patch.object(use_case._video_service, 'update_upload_canceled') as mock_file_service,
            pytest.raises(VideoUploadFailedToAbortError) as e,
        ):
            mock_file_service.return_value = False
            await use_case.execute(command=command)

        await session.refresh(instance=video)
        await session.refresh(instance=video_file)

        mock_file_service.assert_called_once_with(
            id=video.id,
            video_upload_id=video.video_upload_id,
            video_file_id=video_file.id,
        )

        assert e.value.video_id == video.id
        assert e.value.key == video_file.key
        assert e.value.bucket == video_file.bucket
        assert e.value.error_detail == 'video_not_updated'

        assert video.video_upload_status == VideoUploadStatusEnum.UPLOADING.value
        assert video.video_file_id == video_file.id
        assert video.video_upload_id == old_video_upload_id


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_file_not_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        old_video_upload_id = video.video_upload_id

        with (  # noqa: PT012
            patch.object(use_case._file_service, 'delete_by_id') as mock_file_service,
            pytest.raises(VideoUploadFailedToAbortError) as e,
        ):
            mock_file_service.return_value = False
            await use_case.execute(command=command)

        await session.refresh(instance=video)
        await session.refresh(instance=video_file)

        mock_file_service.assert_called_once_with(id=video_file.id)

        assert e.value.video_id == video.id
        assert e.value.key == video_file.key
        assert e.value.bucket == video_file.bucket
        assert e.value.error_detail == 'video_file_not_deleted'

        assert video.video_upload_status == VideoUploadStatusEnum.UPLOADING.value
        assert video.video_file_id == video_file.id
        assert video.video_upload_id == old_video_upload_id
