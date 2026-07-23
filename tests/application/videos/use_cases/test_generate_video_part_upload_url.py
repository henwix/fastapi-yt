from uuid import uuid7

import pytest
from dishka import AsyncContainer
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.use_cases.generate_video_part_upload_url import GenerateVideoPartUploadUrlUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError, VideoUploadAlreadyCompletedError
from app.utils.videos import generate_video_id
from tests.factories.commands.videos import GenerateVideoPartUploadUrlCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_returns_correct_url(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        url = await use_case.execute(command=command)

        assert url.startswith(f'{settings.s3_endpoint}/{settings.s3_private_bucket_name}/{video.s3_key}')
        assert f'uploadId={video.upload_id}' in url
        assert f'partNumber={command.part_number}' in url
        assert f'X-Amz-Credential={settings.s3_access_key}' in url
        assert 'X-Amz-Expires=120' in url


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session, is_active=False)
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)

        command = GenerateVideoPartUploadUrlCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_not_found(container: AsyncContainer):
    async with container() as di:
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
async def test_generate_video_part_upload_url_raises_error_if_access_forbidden(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        author_channel = await ChannelORMFactory.create(session=session)
        second_channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=author_channel.id,
            upload_status=VideoUploadStatusEnum.UPLOADING.value,
            upload_id=uuid7().hex,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(
            current_channel_id=second_channel.id, video_id=video.id
        )

        with pytest.raises(VideoAccessForbiddenError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_already_uploaded(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(GenerateVideoPartUploadUrlUseCase)
        session = await di.get(AsyncSession)

        channel = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=channel.id,
            upload_status=VideoUploadStatusEnum.COMPLETED.value,
            upload_id=uuid7().hex,
        )
        command = GenerateVideoPartUploadUrlCommandFactory.build(current_channel_id=channel.id, video_id=video.id)

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)


@pytest.mark.asyncio
async def test_generate_video_part_upload_url_raises_error_if_video_upload_id_is_none(container: AsyncContainer):
    async with container() as di:
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

        with pytest.raises(VideoUploadAlreadyCompletedError):
            await use_case.execute(command=command)
