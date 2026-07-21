from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.complete_video_multipart_upload import CompleteVideoMultipartUploadUseCase
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError, VideoUploadAlreadyCompletedError
from app.utils.videos import generate_video_id
from tests.factories.commands.videos import CompleteVideoMultipartUploadCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_returns_none_if_completed(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        result = await use_case.execute(command=command)

        assert result is None
        assert video.upload_status == VideoUploadStatusEnum.COMPLETED.value
        assert video.upload_id is None


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)

        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=uuid7(),
            video_id=generate_video_id(),
        )

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=generate_video_id(),
        )

        with pytest.raises(VideoNotFoundError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=second_channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_already_uploaded(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED,
            upload_id=uuid7().hex,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_complete_video_multipart_upload_raises_error_if_video_upload_id_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(CompleteVideoMultipartUploadUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=None,
        )
        command = CompleteVideoMultipartUploadCommandFactory.build(
            current_channel_id=channel.id,
            video_id=video.id,
        )

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)
