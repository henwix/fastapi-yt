from unittest.mock import patch
from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.abort_video_multipart_upload import AbortVideoMultipartUploadUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError, VideoUploadAlreadyCompletedError
from app.infrastructure.sqlalchemy.models.videos import VideoORM
from app.utils.videos import generate_video_id
from tests.factories.commands.videos import AbortVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_upload_aborted(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with patch.object(use_case._task_queue, 'abort_multipart_upload') as mock_task_queue:
            result = await use_case.execute(command=command)

        stmt = select(exists().where(VideoORM.id == video.id))
        sql_result = await session.execute(statement=stmt)

        mock_task_queue.assert_called_once()
        assert result is None
        assert not sql_result.scalar_one()


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)

        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=generate_video_id(),
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_video_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_video_already_uploaded(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            upload_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_abort_video_multipart_upload_returns_none_if_video_upload_id_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(AbortVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=None,
        )
        command = AbortVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)
