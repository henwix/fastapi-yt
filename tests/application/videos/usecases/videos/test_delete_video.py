import pytest
from dishka import AsyncContainer
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.videos.usecases import DeleteVideoUseCase
from app.core.configs import settings
from app.domain.channels.exceptions import ChannelDeletedError, ChannelNotActiveError, ChannelNotFoundByIdError
from app.domain.videos.enums import VideoPrivacyStatusEnum, VideoUploadStatusEnum
from app.domain.videos.exceptions import VideoAccessForbiddenError, VideoNotFoundError
from app.infrastructure.sqlalchemy.models import FileCleanupORM, VideoORM
from app.utils.datetime import get_current_utc_datetime
from tests.factories.commands.videos import DeleteVideoCommandFactory
from tests.factories.models.channels import ChannelORMFactory
from tests.factories.models.videos import VideoORMFactory


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('privacy_status', 'upload_status'),
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
    upload_status: VideoUploadStatusEnum,
):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            privacy_status=privacy_status,
            upload_status=upload_status,
            s3_key=None,
            thumbnail_s3_key=None,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_stmt = select(exists().where(VideoORM.id == video.id))
        file_cleanup_stmt = select(exists(FileCleanupORM))

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_stmt)).scalar_one()
        is_file_cleanup_exists = (await session.execute(statement=file_cleanup_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
        assert not is_file_cleanup_exists


@pytest.mark.asyncio
async def test_delete_video_returns_none_if_deleted_with_video_s3_object(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            thumbnail_s3_key=None,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_stmt = select(exists().where(VideoORM.id == video.id))
        video_file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video.s3_key,
                FileCleanupORM.bucket == settings.s3_private_bucket_name,
            )
        )
        thumbnail_file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video.thumbnail_s3_key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_stmt)).scalar_one()
        is_video_file_cleanup_exists = (await session.execute(statement=video_file_cleanup_stmt)).scalar_one()
        is_thumbnail_file_cleanup_exists = (await session.execute(statement=thumbnail_file_cleanup_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
        assert is_video_file_cleanup_exists
        assert not is_thumbnail_file_cleanup_exists


@pytest.mark.asyncio
async def test_delete_video_returns_none_if_deleted_with_thumbnail_s3_object(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(
            session=session,
            channel_id=video_author.id,
            s3_key=None,
        )

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_stmt = select(exists().where(VideoORM.id == video.id))
        thumbnail_file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video.thumbnail_s3_key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )
        video_file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video.s3_key,
                FileCleanupORM.bucket == settings.s3_private_bucket_name,
            )
        )

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_stmt)).scalar_one()
        is_thumbnail_file_cleanup_exists = (await session.execute(statement=thumbnail_file_cleanup_stmt)).scalar_one()
        is_video_file_cleanup_exists = (await session.execute(statement=video_file_cleanup_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
        assert is_thumbnail_file_cleanup_exists
        assert not is_video_file_cleanup_exists


@pytest.mark.asyncio
async def test_delete_video_returns_none_if_deleted_with_thumbnail_and_video_s3_objects(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        video_author = await ChannelORMFactory.create(session=session)
        video = await VideoORMFactory.create(session=session, channel_id=video_author.id)

        command = DeleteVideoCommandFactory.build(current_channel_id=video_author.id, video_id=video.id)
        video_stmt = select(exists().where(VideoORM.id == video.id))
        thumbnail_file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video.thumbnail_s3_key,
                FileCleanupORM.bucket == settings.s3_public_bucket_name,
            )
        )
        video_file_cleanup_stmt = select(
            exists().where(
                FileCleanupORM.s3_key == video.s3_key,
                FileCleanupORM.bucket == settings.s3_private_bucket_name,
            )
        )

        result = await use_case.execute(command=command)

        is_video_exists = (await session.execute(statement=video_stmt)).scalar_one()
        is_thumbnail_file_cleanup_exists = (await session.execute(statement=thumbnail_file_cleanup_stmt)).scalar_one()
        is_video_file_cleanup_exists = (await session.execute(statement=video_file_cleanup_stmt)).scalar_one()

        assert result is None
        assert not is_video_exists
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

        assert e.value.channel_id == channel.id
        assert e.value.video_id == video.id


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
        channel = await ChannelORMFactory.create(session=session, deleted_at=get_current_utc_datetime())

        command = DeleteVideoCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelDeletedError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_channel_not_active(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)
        session = await di.get(AsyncSession)
        channel = await ChannelORMFactory.create(session=session, is_active=False)

        command = DeleteVideoCommandFactory.build(current_channel_id=channel.id)

        with pytest.raises(ChannelNotActiveError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == channel.id


@pytest.mark.asyncio
async def test_delete_video_raises_error_if_channel_not_found(container: AsyncContainer):
    async with container() as di:
        use_case = await di.get(DeleteVideoUseCase)

        command = DeleteVideoCommandFactory.build()

        with pytest.raises(ChannelNotFoundByIdError) as e:
            await use_case.execute(command=command)

        assert e.value.channel_id == command.current_channel_id
