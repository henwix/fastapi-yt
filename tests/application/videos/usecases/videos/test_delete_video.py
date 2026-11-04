from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoUseCase
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.infrastructure.sqlalchemy.models import FileCleanupORM, FileORM, VideoORM
from tests.factories.commands.videos import DeleteVideoCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('privacy_status', 'video_upload_status'),
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
async def test_delete_video_returns_none_if_deleted_without_s3_objects(
    container: AsyncContainer,
    privacy_status: VideoPrivacyStatusEnum,
    video_upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=privacy_status,
            video_upload_status=video_upload_status,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_stmt = select(exists().where(VideoORM.id == video.id))

        with patch.object(use_case._file_cleanup_service, 'upsert_many') as file_cleanup_service_mock:
            result = await use_case.execute(command=command)

        file_cleanup_service_mock.assert_not_called()
        is_video_exists = (await session.execute(statement=video_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists


@pytest.mark.asyncio
async def test_delete_video_returns_none_if_deleted_with_video_s3_object(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            video_file_id=video_file.id,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_exists_stmt = select(exists().where(VideoORM.id == video.id))
        video_file_exists_stmt = select(
            exists().where(FileORM.key == video_file.key, FileORM.bucket == video_file.bucket)
        )
        video_file_cleanup_exists_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video_file.key,
                FileCleanupORM.bucket == video_file.bucket,
            )
        )

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_exists_stmt)).scalar_one()
        is_video_file_cleanup_exists = (await session.execute(statement=video_file_cleanup_exists_stmt)).scalar_one()
        is_video_file_exists = (await session.execute(statement=video_file_exists_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
        assert not is_video_file_exists
        assert is_video_file_cleanup_exists


@pytest.mark.asyncio
async def test_delete_video_returns_none_if_deleted_with_thumbnail_s3_object(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        thumbnail_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            thumbnail_file_id=thumbnail_file.id,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_exists_stmt = select(exists().where(VideoORM.id == video.id))
        thumbnail_file_exists_stmt = select(
            exists().where(FileORM.key == thumbnail_file.key, FileORM.bucket == thumbnail_file.bucket)
        )
        thumbnail_file_cleanup_exists_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == thumbnail_file.key,
                FileCleanupORM.bucket == thumbnail_file.bucket,
            )
        )

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_exists_stmt)).scalar_one()
        is_thumbnail_file_cleanup_exists = (
            await session.execute(statement=thumbnail_file_cleanup_exists_stmt)
        ).scalar_one()
        is_thumbnail_file_exists = (await session.execute(statement=thumbnail_file_exists_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
        assert not is_thumbnail_file_exists
        assert is_thumbnail_file_cleanup_exists


@pytest.mark.asyncio
async def test_delete_video_returns_none_if_deleted_with_thumbnail_and_video_s3_objects(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video_file = await FileORMFactory.create(session=session)
        thumbnail_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            video_file_id=video_file.id,
            thumbnail_file_id=thumbnail_file.id,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_exists_stmt = select(exists().where(VideoORM.id == video.id))
        thumbnail_file_exists_stmt = select(
            exists().where(FileORM.key == thumbnail_file.key, FileORM.bucket == thumbnail_file.bucket)
        )
        video_file_exists_stmt = select(
            exists().where(FileORM.key == video_file.key, FileORM.bucket == video_file.bucket)
        )
        thumbnail_file_cleanup_exists_stmt = select(
            exists().where(FileCleanupORM.s3_key == thumbnail_file.key, FileCleanupORM.bucket == thumbnail_file.bucket)
        )
        video_file_cleanup_exists_stmt = select(
            exists().where(FileCleanupORM.s3_key == video_file.key, FileCleanupORM.bucket == video_file.bucket)
        )

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_exists_stmt)).scalar_one()
        is_thumbnail_file_exists = (await session.execute(statement=thumbnail_file_exists_stmt)).scalar_one()
        is_video_file_exists = (await session.execute(statement=video_file_exists_stmt)).scalar_one()
        is_thumbnail_file_cleanup_exists = (
            await session.execute(statement=thumbnail_file_cleanup_exists_stmt)
        ).scalar_one()
        is_video_file_cleanup_exists = (await session.execute(statement=video_file_cleanup_exists_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
        assert not is_thumbnail_file_exists
        assert not is_video_file_exists
        assert is_thumbnail_file_cleanup_exists
        assert is_video_file_cleanup_exists


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
