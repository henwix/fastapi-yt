import secrets
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import CompleteVideoMultipartUploadUseCase
from app.core.configs import Settings
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.common.constants import VIDEO_FILE_MIME_TYPES
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import (
    VideoAccessForbiddenError,
    VideoInvalidContentTypeError,
    VideoNotFoundError,
    VideoSizeTooSmallError,
    VideoUploadAlreadyCompletedError,
    VideoUploadNotCreatedError,
)
from app.infrastructure.sqlalchemy.models import FileCleanupORM, FileORM
from tests.factories.commands.videos import CompleteVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=('expected_file_extension', 'expected_file_mime_type'),
    argvalues=[
        ('.mp4', 'video/mp4'),
        ('.mov', 'video/quicktime'),
        ('.mkv', 'video/matroska'),
        ('.mkv', 'video/x-matroska'),
        ('.webm', 'video/webm'),
    ],
)
async def test_complete_video_multipart_upload_returns_none_if_completed(
    mock_container: AsyncContainer,
    test_settings: Settings,
    expected_file_extension: str,
    expected_file_mime_type: str,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)
        use_case._file_type_detector.FILE_TYPE = expected_file_mime_type
        use_case._s3_service.CONTENT_TYPE = expected_file_mime_type

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(
            session=session,
            key=f'videos/{secrets.token_hex(5)}_test.{expected_file_extension}',
            bucket=test_settings.s3_videos_key_prefix,
        )
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        result = await use_case.execute(command=command)

        await session.refresh(instance=video)

        assert result is None
        assert video.video_upload_status == VideoUploadStatusEnum.COMPLETED.value
        assert video.video_upload_id is None
        assert video.video_file_id == video_file.id


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=('expected_file_extension', 'expected_file_mime_type'),
    argvalues=[
        ('.mp4', 'image/png'),
        ('.mp4', 'image/jpeg'),
        ('.mp4', 'video/matroska'),
        ('.mov', 'video/mp4'),
        ('.mov', 'video/x-matroska'),
        ('.mov', 'image/png'),
        ('.mkv', 'video/webm'),
        ('.mkv', 'video/mp4'),
        ('.webm', 'image/gif'),
        ('.webm', 'image/jpeg'),
    ],
)
async def test_complete_video_multipart_upload_raises_error_if_video_file_metadata_mime_type_invalid(
    mock_container: AsyncContainer,
    test_settings: Settings,
    expected_file_extension: str,
    expected_file_mime_type: str,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)
        use_case._file_type_detector.FILE_TYPE = VIDEO_FILE_MIME_TYPES[expected_file_extension][0]
        use_case._s3_service.CONTENT_TYPE = expected_file_mime_type

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(
            session=session,
            key=f'videos/{secrets.token_hex(5)}_test.{expected_file_extension}',
            bucket=test_settings.s3_videos_key_prefix,
        )
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoInvalidContentTypeError) as e:
            await use_case.execute(command=command)

        await session.refresh(instance=video)

        assert e.value.actual_content_type == VIDEO_FILE_MIME_TYPES[expected_file_extension][0]
        assert e.value.metadata_content_type == expected_file_mime_type
        assert video.video_upload_status == VideoUploadStatusEnum.PENDING.value
        assert video.video_upload_id is None
        assert video.video_file_id is None

        video_file_exists_stmt = select(exists().where(FileORM.id == video_file.id))
        video_file_cleanup_exists_stmt = select(
            exists().where(FileCleanupORM.s3_key == video_file.key, FileCleanupORM.bucket == video_file.bucket)
        )
        assert not (await session.execute(statement=video_file_exists_stmt)).scalar_one()
        assert (await session.execute(statement=video_file_cleanup_exists_stmt)).scalar_one()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    argnames=('expected_file_extension', 'expected_file_mime_type'),
    argvalues=[
        ('.mp4', 'image/png'),
        ('.mp4', 'image/jpeg'),
        ('.mp4', 'video/matroska'),
        ('.mov', 'video/mp4'),
        ('.mov', 'video/x-matroska'),
        ('.mov', 'image/png'),
        ('.mkv', 'video/webm'),
        ('.mkv', 'video/mp4'),
        ('.webm', 'image/gif'),
        ('.webm', 'image/jpeg'),
    ],
)
async def test_complete_video_multipart_upload_raises_error_if_video_file_actual_mime_type_invalid(
    mock_container: AsyncContainer,
    test_settings: Settings,
    expected_file_extension: str,
    expected_file_mime_type: str,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)
        use_case._file_type_detector.FILE_TYPE = expected_file_mime_type
        use_case._s3_service.CONTENT_TYPE = VIDEO_FILE_MIME_TYPES[expected_file_extension][0]

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(
            session=session,
            key=f'videos/{secrets.token_hex(5)}_test.{expected_file_extension}',
            bucket=test_settings.s3_videos_key_prefix,
        )
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoInvalidContentTypeError) as e:
            await use_case.execute(command=command)

        await session.refresh(instance=video)

        assert e.value.metadata_content_type == VIDEO_FILE_MIME_TYPES[expected_file_extension][0]
        assert e.value.actual_content_type == expected_file_mime_type
        assert video.video_upload_status == VideoUploadStatusEnum.PENDING.value
        assert video.video_upload_id is None
        assert video.video_file_id is None

        video_file_exists_stmt = select(exists().where(FileORM.id == video_file.id))
        video_file_cleanup_exists_stmt = select(
            exists().where(FileCleanupORM.s3_key == video_file.key, FileCleanupORM.bucket == video_file.bucket)
        )
        assert not (await session.execute(statement=video_file_exists_stmt)).scalar_one()
        assert (await session.execute(statement=video_file_cleanup_exists_stmt)).scalar_one()


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_file_size_too_small(
    mock_container: AsyncContainer, test_settings: Settings
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)
        use_case._s3_service.CONTENT_LENGTH = 0

        channel = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(
            session=session,
            key=f'videos/{secrets.token_hex(5)}_test.mp4',
            bucket=test_settings.s3_videos_key_prefix,
        )
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_file_id=video_file.id,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoSizeTooSmallError) as e:
            await use_case.execute(command=command)

        old_video_key = video_file.key
        await session.refresh(instance=video)

        assert e.value.bucket == test_settings.s3_private_bucket_name
        assert e.value.key == old_video_key
        assert e.value.file_size == 0
        assert video.video_upload_status == VideoUploadStatusEnum.PENDING.value
        assert video.video_upload_id is None
        assert video.video_file_id is None

        video_file_exists_stmt = select(exists().where(FileORM.id == video_file.id))
        video_file_cleanup_exists_stmt = select(
            exists().where(FileCleanupORM.s3_key == video_file.key, FileCleanupORM.bucket == video_file.bucket)
        )
        assert not (await session.execute(statement=video_file_exists_stmt)).scalar_one()
        assert (await session.execute(statement=video_file_cleanup_exists_stmt)).scalar_one()


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_channel_not_active(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = CompleteVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_channel_deleted(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)
        command = CompleteVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_channel_deletetion_status_purging(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session,
            deletion_status=ChannelDeletionStatusEnum.PURGING.value,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_channel_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)

        command = CompleteVideoMultipartUploadCommandFactory.build(current_channel_id=uuid7())

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_not_found(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = CompleteVideoMultipartUploadCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_access_forbidden(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_already_uploaded(mock_container: AsyncContainer):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.COMPLETED.value,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_upload_not_created_and_status_pending(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.PENDING.value,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_uploading_and_upload_id_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
            video_upload_id=None,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_uploading_and_s3_key_is_none(
    mock_container: AsyncContainer,
):
    async with mock_container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            video_upload_status=VideoUploadStatusEnum.UPLOADING.value,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadNotCreatedError):
            await use_case.execute(command=command)
