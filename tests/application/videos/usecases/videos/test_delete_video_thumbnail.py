from unittest.mock import patch

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoThumbnailUseCase
from app.domain.channels.enums import ChannelDeletionStatusEnum
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.files_cleanup.enums import FileCleanupStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError, VideoThumbnailNotFoundError
from app.infrastructure.sqlalchemy.models import FileCleanupORM, FileORM
from tests.factories.commands.videos.videos import DeleteVideoThumbnailCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.files import FileORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_delete_video_thumbnail_returns_none_if_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        thumbnail_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            thumbnail_file_id=thumbnail_file.id,
        )

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        thumbnail_file_exists_stmt = select(
            exists().where(FileORM.key == thumbnail_file.key, FileORM.bucket == thumbnail_file.bucket)
        )
        thumbnail_file_cleanup_stmt = select(FileCleanupORM).where(
            FileCleanupORM.s3_key == thumbnail_file.key, FileCleanupORM.bucket == thumbnail_file.bucket
        )

        result = await use_case.execute(command=command)

        await session.refresh(instance=video)

        assert result is None
        assert video.thumbnail_file_id is None
        assert not (await session.execute(statement=thumbnail_file_exists_stmt)).scalar_one()

        thumbnail_file_cleanup = (await session.execute(statement=thumbnail_file_cleanup_stmt)).scalar_one()
        assert thumbnail_file_cleanup.error_code is None
        assert thumbnail_file_cleanup.error_message is None
        assert thumbnail_file_cleanup.locked_until is None
        assert thumbnail_file_cleanup.status == FileCleanupStatusEnum.PENDING.value


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_thumbnail_file_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=channel.id)

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoThumbnailNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_thumbnail_file_not_found_in_db(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        thumbnail_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            thumbnail_file_id=thumbnail_file.id,
        )

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with (  # noqa: PT012
            pytest.raises(VideoThumbnailNotFoundError) as e,
            patch.object(use_case._file_service, 'get_by_id') as file_service_mock,
        ):
            file_service_mock.return_value = None
            await use_case.execute(command=command)

        await session.refresh(instance=video)
        await session.refresh(instance=thumbnail_file)

        file_service_mock.assert_called_once_with(id=thumbnail_file.id)
        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_thumbnail_file_not_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        thumbnail_file = await FileORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            thumbnail_file_id=thumbnail_file.id,
        )

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with (  # noqa: PT012
            pytest.raises(VideoThumbnailNotFoundError) as e,
            patch.object(use_case._file_service, 'delete_by_id') as file_service_mock,
        ):
            file_service_mock.return_value = False
            await use_case.execute(command=command)

        await session.refresh(instance=thumbnail_file)

        file_service_mock.assert_called_once_with(id=thumbnail_file.id)
        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_video_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        author_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
        )

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoAccessForbiddenError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id
        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(VideoNotFoundError) as e:
            await use_case.execute(command=command)

        assert e.value.video_id == command.video_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_channel_deleted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create_deleted(session=session)

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_channel_deletion_status_purging(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(
            session=session, deletion_status=ChannelDeletionStatusEnum.PURGING.value
        )

        command = DeleteVideoThumbnailCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id


@pytest.mark.asyncio
async def test_delete_video_thumbnail_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoThumbnailUseCase)

        command = DeleteVideoThumbnailCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
